import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import base64
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
import wsgiref.simple_server

from edith.lib.shared.models.email import EmailMessage
from edith.config import EmailAssistantConfig

class GmailService:
    def __init__(self, config: EmailAssistantConfig):
        self.config = config
        self.service = None
        self.creds = None
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
                       'https://www.googleapis.com/auth/calendar.readonly']
        
    def authenticate(self) -> bool:
        creds = None
        # Use a safe filename for the token
        primary_email = self.config.get_primary_email()
        token_filename = f"token_{primary_email}.json" if primary_email else "token.json"
        
        if os.path.exists(token_filename):
            try:
                creds = Credentials.from_authorized_user_file(token_filename, self.SCOPES)
            except Exception as e:
                print(f"Error loading token (will re-authenticate): {e}")
                creds = None
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.config.gmail_credentials_path):
                    print(f"\n❌ Error: '{self.config.gmail_credentials_path}' not found.")
                    print("   Please download the OAuth 2.0 Client ID JSON from Google Cloud Console")
                    print(f"   and save it as '{self.config.gmail_credentials_path}' in the project root.")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.gmail_credentials_path, self.SCOPES)
                creds = self._authenticate_headless(flow, port=8080)
                
            # Save the credentials for the next run
            with open(token_filename, 'w') as token:
                token.write(creds.to_json())
                
        self.creds = creds
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    def _authenticate_headless(self, flow, port=8080):
        """
        Custom authentication flow for headless/Docker environments.
        Listens on 0.0.0.0 (for Docker) but tells Google to redirect to localhost.
        """
        flow.redirect_uri = f'http://localhost:{port}/'
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        print(f"\n⚠️  HEADLESS AUTHENTICATION REQUIRED ⚠️")
        print(f"1. Open this URL in your browser:\n{auth_url}")
        print(f"2. Log in and allow access.")
        print(f"3. The browser will redirect to localhost:{port}, which Docker will catch.")
        
        auth_code = None
        
        def app(environ, start_response):
            nonlocal auth_code
            query = environ.get('QUERY_STRING', '')
            params = {}
            for p in query.split('&'):
                if '=' in p:
                    k, v = p.split('=', 1)
                    params[k] = v
            
            code = params.get('code')
            if code:
                auth_code = code
                start_response('200 OK', [('Content-Type', 'text/html')])
                return [b'<h1>Authentication Successful!</h1><p>You can close this window and return to the terminal.</p>']
            
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Not Found']

        server = wsgiref.simple_server.make_server('0.0.0.0', port, app)
        # Set a timeout to prevent hanging on browser pre-connections or keep-alive
        server.socket.settimeout(1.0)
        # Suppress error logs from timeouts/pre-connects
        server.handle_error = lambda request, client_address: None
        
        # Keep handling requests until we get the auth code
        while auth_code is None:
            # handle_request may timeout if no connection, which is fine
            server.handle_request()
        
        flow.fetch_token(code=auth_code)
        return flow.credentials

    def get_emails(self, max_results: int = 50, query: str = "newer_than:30d", page_token: str = None, exclude_noise: bool = True) -> Tuple[List[EmailMessage], Optional[str]]:
        if not self.service:
            raise Exception("Not authenticated")
            
        try:
            if exclude_noise:
                # Filter out noise (Promotions, Social, Spam) at the provider level
                query = f"{query} -category:promotions -category:social -in:spam -in:trash"

            print(f"   [Gmail] Fetching list of {max_results} messages...")
            result = self.service.users().messages().list(
                userId='me', maxResults=max_results, q=query, pageToken=page_token).execute()
            messages = result.get('messages', [])
            print(f"   [Gmail] Found {len(messages)} messages. Downloading details...")
            
            email_messages = []
            
            if not messages:
                return [], result.get('nextPageToken')

            # Use BatchHttpRequest to fetch details in parallel
            def callback(request_id, response, exception):
                if exception:
                    print(f"Error fetching email details: {exception}")
                else:
                    email_data = self._parse_email(response)
                    if email_data:
                        email_messages.append(email_data)

            # Process in chunks to avoid Rate Limit (429)
            BATCH_SIZE = 15
            for i in range(0, len(messages), BATCH_SIZE):
                batch = self.service.new_batch_http_request(callback=callback)
                chunk = messages[i:i + BATCH_SIZE]
                
                for message in chunk:
                    batch.add(self.service.users().messages().get(userId='me', id=message['id'], format='full'))
                    
                batch.execute()
            print(f"   [Gmail] Successfully parsed {len(email_messages)} emails.")
            
            return email_messages, result.get('nextPageToken')
        except HttpError as e:
            if e.resp.status == 403 and 'accessNotConfigured' in str(e):
                print(f"\n❌ CRITICAL: Gmail API is not enabled for this project.")
                print(f"   Please enable it in the Google Cloud Console (see URL in error details below).")
            print(f"Error fetching emails: {e}")
            return [], None
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return [], None
    
    def get_profile_email(self) -> str:
        if not self.service:
            raise Exception("Not authenticated")
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile['emailAddress']
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return "unknown@gmail.com"
    
    def _parse_email(self, msg: Dict[str, Any]) -> Optional[EmailMessage]:
        try:
            headers = msg['payload']['headers']
            subject = ""
            sender = ""
            date_str = ""
            
            for header in headers:
                if header['name'].lower() == 'subject':
                    subject = header['value']
                elif header['name'].lower() == 'from':
                    sender = header['value']
                elif header['name'].lower() == 'date':
                    date_str = header['value']
            
            # Extract email body
            body = self._get_email_body(msg['payload'])
            
            # Parse date
            try:
                date = parsedate_to_datetime(date_str)
            except Exception:
                # Fallback if date parsing fails
                date = datetime.now()
            
            return EmailMessage(
                id=msg['id'],
                subject=subject,
                sender=sender,
                body=body,
                date=date,
                account_type="personal",  # Default for MVP
                labels=msg.get('labelIds', [])
            )
        except Exception as e:
            print(f"Error parsing email: {e}")
            return None
    
    def _get_email_body(self, payload: Dict[str, Any]) -> str:
        if 'parts' in payload:
            # Multipart email
            body = ""
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    # Fix padding for base64 decoding
                    data += '=' * (-len(data) % 4)
                    body += base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
                elif part['mimeType'] == 'text/html':
                    data = part['body']['data']
                    data += '=' * (-len(data) % 4)
                    html_content = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
                    # If we haven't found plain text yet, or if we want to append cleaned HTML
                    if not body:
                        soup = BeautifulSoup(html_content, 'html.parser')
                        body = soup.get_text(separator=' ', strip=True)
            return body.strip()
        else:
            # Single part email
            data = payload['body']['data']
            data += '=' * (-len(data) % 4)
            content = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            if payload['mimeType'] == 'text/html':
                soup = BeautifulSoup(content, 'html.parser')
                return soup.get_text(separator=' ', strip=True)
            return content