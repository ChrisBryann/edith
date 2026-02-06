from typing import List, Tuple, Optional
from datetime import datetime
from edith.lib.shared.models.email import EmailMessage
from edith.config import EmailAssistantConfig
from edith.mocks.store import MockDataStore

class DummyEmailFetcher:
    def __init__(self, config: EmailAssistantConfig):
        self.config = config
        self.store = MockDataStore()
        self.creds = "mock_creds" # Dummy value to pass checks if needed, or None

    def get_emails(self, max_results: int = 50, query: str = "newer_than:30d", page_token: str = None, exclude_noise: bool = True) -> Tuple[List[EmailMessage], Optional[str]]:
        raw_emails = self.store.get_emails()
        
        email_messages = []
        for e in raw_emails:
            msg = EmailMessage(
                id=e["id"],
                thread_id=e.get("thread_id", e["id"]),  # Use email ID as thread_id if not present
                sender=e["sender"],
                to_emails=e.get("to_emails", ["alex@techflow.com"]),  # Default recipient
                cc_emails=e.get("cc_emails", []),
                subject=e["subject"],
                body=e["body"],
                date=datetime.fromisoformat(e["date"]),
                is_unread=e.get("is_unread", False),
                headers=e.get("headers", {}),
                is_relevant=True,
                account_type="work" if "work" in e.get("account_source", "") else "personal"
            )
            email_messages.append(msg)
            
        return email_messages[:max_results], None

    def authenticate(self):
        return True

    def get_profile_email(self):
        return "alex@techflow.com"
