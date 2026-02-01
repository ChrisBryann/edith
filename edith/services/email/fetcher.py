from typing import List, Tuple, Optional
from edith.config import EmailAssistantConfig
from edith.models import EmailMessage
from edith.services.email.providers.gmail import GmailService

class EmailFetcher:
    def __init__(self, config: EmailAssistantConfig):
        self.config = config
        # In the future, this could be a map of providers or factory
        self.gmail_provider = GmailService(config)

    def authenticate(self) -> bool:
        # For MVP, just authenticate Gmail
        return self.gmail_provider.authenticate()

    def get_profile_email(self) -> str:
        return self.gmail_provider.get_profile_email()
        
    def get_emails(self, max_results: int = 50, query: str = "newer_than:30d", page_token: str = None, exclude_noise: bool = True) -> Tuple[List[EmailMessage], Optional[str]]:
        return self.gmail_provider.get_emails(max_results, query, page_token, exclude_noise)
    
    @property
    def creds(self):
        return self.gmail_provider.creds