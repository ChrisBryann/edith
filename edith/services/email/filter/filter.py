import re, logging
from typing import List
from datetime import datetime, timedelta

from edith.services.email.filter.constants import SPAM_KEYWORDS, IMPORTANT_SENDERS, IMPORTANT_SUBJECTS, LIST_HEADER_KEYS, ZERO_SHOT_SPAM_LABELS

from edith.lib.shared.models.email import EmailMessage
from edith.config import EmailAssistantConfig
from edith.lib.shared.llm.spam_service import SpamLLMService

logger = logging.getLogger(__name__)

class EmailFilter:
    def __init__(self, config: EmailAssistantConfig):
        self.spam_service = SpamLLMService(config)
        
    def filter_relevant_emails(self, emails: List[EmailMessage]) -> List[EmailMessage]:
        """Filter relevant emails by sequential filtering using Heuristics and LLM Detection"""
        relevant_emails_idx = []
        relevant_ham_emails = []
        
        # filter by heuristics scoring first
        for i, email in enumerate(emails):
            if self._is_relevant(email):
                relevant_emails_idx.append(i)
                
        # then, filter again the emails that pass heuristics through LLM detection
        for idx in relevant_emails_idx:
            if not self._is_spam_ml(emails[idx]):
                emails[idx].is_relevant = True
                relevant_ham_emails.append(emails[idx])
        
        return relevant_ham_emails
    
    
    def _is_relevant(self, email: EmailMessage) -> bool:
        # 1. Immediate Qualifiers: Always keep emails from important senders
        if self._is_important_sender(email.sender):
            return True
        
        # 2. Immediate Disqualifiers: Filter out known noise
        
        # A. Gmail Categories (Provider-Specific High Confidence)
        if email.labels:
            # Filter out explicit Promotions and Social categories
            if 'CATEGORY_PROMOTIONS' in email.labels or 'CATEGORY_SOCIAL' in email.labels:
                return False
        
        # B. Generic Spam/Marketing Detection (Crucial for non-Gmail providers)
        if self._is_spam(email):
            return False
        
        # C. Mailing List (No need to notice advertisement emails)
        if self._is_mailing_list(email.headers):
            return False

        # 3. Content Qualifiers: If it's not spam, is it important?
        
        if self._contains_important_keywords(email.subject):
            return True
        
        if email.subject.lower().startswith('re:'):
            return True
        
        if self._contains_important_content(email.body):
            return True
        
        # 4. Fallback: If it passed spam checks and is recent, keep it.
        if self._is_recent_email(email.date):
            return True
        
        return False
    
    def _is_important_sender(self, sender: str) -> bool:
        return self._contains_any_keyword(sender, IMPORTANT_SENDERS)
    
    def _contains_important_keywords(self, subject: str) -> bool:
        return self._contains_any_keyword(subject, IMPORTANT_SUBJECTS)
    
    def _is_recent_email(self, date: datetime) -> bool:
        now = datetime.now()
        if date.tzinfo:
            now = now.astimezone()
        thirty_days_ago = now - timedelta(days=30)
        return date > thirty_days_ago
    
    def _is_spam(self, email: EmailMessage) -> bool:
        # Check subject for spam keywords
        if self._contains_any_keyword(email.subject, SPAM_KEYWORDS):
            return True
        
        # Check sender for spam patterns
        # Removed 'noreply' as it is often used for receipts/tickets
        if self._contains_any_keyword(email.sender, {"marketing"}):
            return True
        
        # Check if email has many recipients (likely marketing)
        # This would require additional parsing of headers
        
        # Check body for common marketing footers (Universal fallback for non-Gmail)
        if self._contains_any_keyword(email.body, {'unsubscribe', 'view in browser', 'update preferences'}):
            return True
        
        return False

    def _is_spam_ml(self, email: EmailMessage) -> bool:
        """Uses DistillBERT to classify emails as spam or not"""
        try:
            
            ml_results = self.spam_service.detect_spam([f'Subject: {email.subject}\n\n{email.body[:512]}'])
            
            assert len(ml_results) > 0
            
            return ml_results[0].label == "Spam"
        except Exception as e:
            logging.error(f"Error classifying email: {e}")
        
        return False

    def _is_spam_ml_zero_shot(self, email: EmailMessage) -> bool:
        """Uses Zero Shot Classification with MNNLI to classify emails as spam or not"""
        try:
            
            ml_results = self.spam_service.detect_spam_zero_shot(f'Subject: {email.subject}\n\n{email.body[:512]}')
            print(ml_results)
            return ml_results.label in ZERO_SHOT_SPAM_LABELS
        
        except Exception as e:
            logging.error(f"Error classifying email: {e}")
        
        return False

    def _contains_important_content(self, body: str) -> bool:
        body_lower = body.lower()
        
        # Look for action items or important content
        action_patterns = [
            r'\bplease\b.*\b(action|review|respond|call|meet)\b',
            r'\b(need|required|must|should)\b',
            r'\b(deadline|due|meeting|call|appointment)\b',
            r'\b(attachment|attached|document|file)\b'
        ]
        
        for pattern in action_patterns:
            if re.search(pattern, body_lower):
                return True
        
        return False
    
    def _is_mailing_list(self, headers: dict) -> bool:
        """Is email part of mailing list"""
        keys = {k.lower() for k in headers.keys()}
        if keys & LIST_HEADER_KEYS:
            return True
        prec = headers.get("Precedence") or headers.get("precedence")
        return (prec or "").lower() in {"bulk", "list", "junk"}
    
    def add_important_sender(self, sender: str):
        if sender not in IMPORTANT_SENDERS:
            IMPORTANT_SENDERS.append(sender)
    
    def add_important_subject_keyword(self, keyword: str):
        if keyword not in IMPORTANT_SUBJECTS:
            IMPORTANT_SUBJECTS.append(keyword)
            
    # --- Helper Functions ---
    
    def _contains_any_keyword(self, text: str, keywords: set[str]) -> bool:
        t = (text or "").lower()
        return any(k.lower() in t for k in keywords)