from cryptography.fernet import Fernet
import base64
import os

class DataEncryptor:
    """
    Handles encryption and decryption of sensitive data at rest.
    Uses Fernet (symmetric encryption).
    """
    def __init__(self, key: str = None):
        if not key:
            # Check environment variable
            key = os.getenv("EDITH_ENCRYPTION_KEY")
        
        if not key:
            # Fallback for dev/demo if not set (NOT SECURE but functional)
            print("⚠️  SECURITY WARNING: EDITH_ENCRYPTION_KEY not set. Using insecure default key for development.")
            # 32-byte key for Fernet
            key = base64.urlsafe_b64encode(b"edith_insecure_dev_key_000000000")
            
        self.fernet = Fernet(key)

    def encrypt(self, text: str) -> str:
        if not text: return ""
        return self.fernet.encrypt(text.encode()).decode()

    def decrypt(self, token: str) -> str:
        if not token: return ""
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except Exception:
            return "[Decryption Failed]"