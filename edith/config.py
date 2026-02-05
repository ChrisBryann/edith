import os
from typing import List
from edith.lib.shared.models.email import EmailConfig
from edith.lib.shared.models.util import Environment

class EmailAssistantConfig:
    def __init__(self):
        # Determine Environment
        env_str = os.getenv("EDITH_ENV", "dev").lower()
        try:
            self.env = Environment(env_str)
        except ValueError:
            self.env = Environment.DEV

        self.email_accounts: List[EmailConfig] = []
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gmail_credentials_path = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.encryption_key = os.getenv("EDITH_ENCRYPTION_KEY")
        self.chroma_server_host = os.getenv("CHROMA_SERVER_HOST")
        self.chroma_server_port = int(os.getenv("CHROMA_SERVER_PORT", 8000))
        
        self.spam_detection_model_id = os.getenv("SPAM_DETECTION_MODEL_ID")
        self.spam_zs_detection_model_id = os.getenv("SPAM_ZS_DETECTION_MODEL_ID")
        self.hf_token = os.getenv('HF_TOKEN')

        
        # Environment Configuration
        if self.env == Environment.TEST:
            self.chroma_db_path = "./test_chroma_db"
            self.use_mock_data = True
        elif self.env == Environment.DEV:
            self.chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
            self.use_mock_data = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
        else: # PROD
            self.chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
            self.use_mock_data = False
        
    def add_email_account(self, email_address: str, is_primary: bool = False, account_type: str = "personal"):
        config = EmailConfig(email_address=email_address, is_primary=is_primary, account_type=account_type)
        self.email_accounts.append(config)
        
    def get_primary_email(self) -> str | None:
        for config in self.email_accounts:
            if config.is_primary:
                return config.email_address
        return self.email_accounts[0].email_address if self.email_accounts else None