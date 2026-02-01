import re
from typing import List, Dict, Tuple

class PIIScrubber:
    """
    Basic PII (Personally Identifiable Information) redaction service.
    Used to sanitize text before sending it to external LLM providers.
    """
    
    def __init__(self):
        # Compiled regex patterns for performance
        self.patterns = {
            # Basic Email Regex
            'EMAIL': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            # Phone Number (Supports various formats like +1-555-555-5555 or (555) 555-5555)
            'PHONE': re.compile(r'\b(\+\d{1,2}\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b'),
            # SSN (Simple US format)
            'SSN': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            # IPv4 Address
            'IP_ADDRESS': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
        }

    def scrub(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Replaces PII with unique placeholders (e.g., <EMAIL_1>) and returns
        a mapping to restore them later.
        """
        mapping = {}
        scrubbed_text = text
        
        for label, pattern in self.patterns.items():
            # We use a closure to maintain state (mapping) during substitution
            def replace_fn(match):
                original_value = match.group(0)
                
                # Check if we've already assigned a placeholder for this value
                # (Consistency: john@doe.com should always be <EMAIL_1>)
                for placeholder, original in mapping.items():
                    if original == original_value:
                        return placeholder
                
                # Create new placeholder
                placeholder = f"<{label}_{len(mapping) + 1}>"
                mapping[placeholder] = original_value
                return placeholder

            scrubbed_text = pattern.sub(replace_fn, scrubbed_text)
            
        return scrubbed_text, mapping

    def restore(self, text: str, mapping: Dict[str, str]) -> str:
        """Restores PII from placeholders using the provided mapping."""
        restored_text = text
        for placeholder, original in mapping.items():
            restored_text = restored_text.replace(placeholder, original)
        return restored_text