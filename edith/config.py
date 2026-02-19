import os
from typing import List, Optional
from edith.lib.shared.models.email import EmailConfig
from edith.lib.shared.models.util import Environment

class EmailAssistantConfig:
    def __init__(self):
        # Determine Environment
        env_str = self.get_env("EDITH_ENV", "dev").lower()
        self.base_url = self.get_env("BASE_URL", "http://localhost:8000")
        try:
            self.env = Environment(env_str)
        except ValueError:
            self.env = Environment.DEV

        self.email_accounts: List[EmailConfig] = []
        self.gemini_api_key = self.get_env("GEMINI_API_KEY")
        self.gmail_credentials_path = self.get_env("GMAIL_CREDENTIALS_PATH", "credentials.json")
        self.gemini_model = self.get_env("GEMINI_MODEL", "gemini-2.5-flash")
        self.encryption_key = self.get_env("EDITH_ENCRYPTION_KEY")
        self.chroma_server_host = self.get_env("CHROMA_SERVER_HOST")
        self.chroma_server_port = int(self.get_env("CHROMA_SERVER_PORT", 8000))
        
        self.spam_detection_model_id = self.get_env("SPAM_DETECTION_MODEL_ID")
        self.spam_zs_detection_model_id = self.get_env("SPAM_ZS_DETECTION_MODEL_ID")
        self.hf_token = self.get_env('HF_TOKEN')
        
        self.yahoo_client_id = self.get_env('YAHOO_CLIENT_ID')
        self.yahoo_client_secret = self.get_env('YAHOO_CLIENT_SECRET')

        
        # Environment Configuration
        if self.env == Environment.TEST:
            self.chroma_db_path = "./test_chroma_db"
            self.use_mock_data = True
        elif self.env == Environment.DEV:
            self.chroma_db_path = self.get_env("CHROMA_DB_PATH", "./chroma_db")
            self.use_mock_data = self.get_env("USE_MOCK_DATA", "false").lower() == "true"
        else: # PROD
            self.chroma_db_path = self.get_env("CHROMA_DB_PATH", "./chroma_db")
            self.use_mock_data = False
            
    def get_env(self, name: str, fallback: str = "") -> str:
        value = os.getenv(name, fallback)
        if value == fallback:
            return fallback
        if not value:
            raise RuntimeError(f"{name} environment variable is required")
        return value

        
    def add_email_account(self, email_address: str, is_primary: bool = False, account_type: str = "personal"):
        config = EmailConfig(email_address=email_address, is_primary=is_primary, account_type=account_type)
        self.email_accounts.append(config)
        
    def get_primary_email(self) -> str | None:
        for config in self.email_accounts:
            if config.is_primary:
                return config.email_address
        return self.email_accounts[0].email_address if self.email_accounts else None