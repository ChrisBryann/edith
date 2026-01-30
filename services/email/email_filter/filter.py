import re
from typing import List
from datetime import datetime, timedelta

from lib.shared.models import EmailMessage

class EmailFilter:
    def __init__(self):
        self.spam_keywords = [
            'unsubscribe', 'promotion', 'sale', 'discount', 'offer', 'deal',
            'marketing', 'newsletter', 'advertisement', 'sponsored', 'free trial'
        ]
        
        self.important_senders = [
            # Users can customize this list
        ]
        
        self.important_subjects = [
            'meeting', 'deadline', 'urgent', 'important', 'assignment',
            'project', 'schedule', 'appointment', 'interview'
        ]
    
    def filter_relevant_emails(self, emails: List[EmailMessage]) -> List[EmailMessage]:
        relevant_emails = []
        
        for email in emails:
            if self._is_relevant(email):
                email.is_relevant = True
                relevant_emails.append(email)
        
        return relevant_emails
    
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
        sender_lower = sender.lower()
        return any(keyword.lower() in sender_lower for keyword in self.important_senders)
    
    def _contains_important_keywords(self, subject: str) -> bool:
        subject_lower = subject.lower()
        return any(keyword.lower() in subject_lower for keyword in self.important_subjects)
    
    def _is_recent_email(self, date: datetime) -> bool:
        now = datetime.now()
        if date.tzinfo:
            now = now.astimezone()
        thirty_days_ago = now - timedelta(days=30)
        return date > thirty_days_ago
    
    def _is_spam(self, email: EmailMessage) -> bool:
        # Check subject for spam keywords
        subject_lower = email.subject.lower()
        if any(keyword.lower() in subject_lower for keyword in self.spam_keywords):
            return True
        
        # Check sender for spam patterns
        sender_lower = email.sender.lower()
        # Removed 'noreply' as it is often used for receipts/tickets
        if any(pattern in sender_lower for pattern in ['marketing']):
            return True
        
        # Check if email has many recipients (likely marketing)
        # This would require additional parsing of headers
        
        # Check body for common marketing footers (Universal fallback for non-Gmail)
        body_lower = email.body.lower()
        if 'unsubscribe' in body_lower or 'view in browser' in body_lower or 'update preferences' in body_lower:
            return True
        
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
    
    def add_important_sender(self, sender: str):
        if sender not in self.important_senders:
            self.important_senders.append(sender)
    
    def add_important_subject_keyword(self, keyword: str):
        if keyword not in self.important_subjects:
            self.important_subjects.append(keyword)