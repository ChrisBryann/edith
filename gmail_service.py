import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from typing import List, Dict, Any, Optional
from datetime import datetime
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials

from config import EmailMessage, EmailAssistantConfig

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
            creds = Credentials.from_authorized_user_file(token_filename, self.SCOPES)
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.gmail_credentials_path, self.SCOPES)
                # Use fixed port 8080 to match redirect URIs often set in Google Cloud
                creds = flow.run_local_server(port=8080)
                
            # Save the credentials for the next run
            with open(token_filename, 'w') as token:
                token.write(creds.to_json())
                
        self.creds = creds
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    def get_emails(self, max_results: int = 50) -> List[EmailMessage]:
        if not self.service:
            raise Exception("Not authenticated")
            
        try:
            result = self.service.users().messages().list(
                userId='me', maxResults=max_results).execute()
            messages = result.get('messages', [])
            
            email_messages = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id'], format='full').execute()
                
                email_data = self._parse_email(msg)
                if email_data:
                    email_messages.append(email_data)
                    
            return email_messages
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
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
                account_type="personal"  # Default for MVP
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
                    body += base64.urlsafe_b64decode(data).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    data = part['body']['data']
                    data += '=' * (-len(data) % 4)
                    html_content = base64.urlsafe_b64decode(data).decode('utf-8')
                    # If we haven't found plain text yet, or if we want to append cleaned HTML
                    if not body:
                        soup = BeautifulSoup(html_content, 'html.parser')
                        body = soup.get_text(separator=' ', strip=True)
            return body.strip()
        else:
            # Single part email
            data = payload['body']['data']
            data += '=' * (-len(data) % 4)
            content = base64.urlsafe_b64decode(data).decode('utf-8')
            if payload['mimeType'] == 'text/html':
                soup = BeautifulSoup(content, 'html.parser')
                return soup.get_text(separator=' ', strip=True)
            return content