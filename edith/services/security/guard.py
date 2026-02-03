import re
import logging
import unicodedata

logger = logging.getLogger(__name__)

class PromptGuard:
    """
    Service to detect and mitigate prompt injection attacks in ingested content.
    Acts as a firewall for untrusted data before it enters the RAG system.
    """
    def __init__(self):
        # Regex patterns for common injection attempts
        # These catch phrases often used to override system prompts
        self.risk_patterns = [
            re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
            re.compile(r"ignore\s+system\s+prompt", re.IGNORECASE),
            re.compile(r"you\s+are\s+now\s+a", re.IGNORECASE),
            re.compile(r"override\s+system", re.IGNORECASE),
            re.compile(r"simulat(e|ing)\s+mode", re.IGNORECASE),
            re.compile(r"jailbreak", re.IGNORECASE),
            re.compile(r"DAN\s+mode", re.IGNORECASE),
            re.compile(r"system\s+override", re.IGNORECASE),
        ]

    def validate(self, text: str) -> bool:
        """
        Checks text for prompt injection patterns.
        Returns True if safe, False if suspicious.
        """
        # Zero Trust: Normalize to NFKC form to catch homoglyphs and invisible characters
        # e.g. "ｉｇｎｏｒｅ" (Full-width) -> "ignore" (Latin)
        text = unicodedata.normalize('NFKC', text)
        
        for pattern in self.risk_patterns:
            if pattern.search(text):
                return False
        return True