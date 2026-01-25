import re
from typing import List
from datetime import datetime, timedelta

from config import EmailMessage

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
        # Check if it's from an important sender
        if self._is_important_sender(email.sender):
            return True
        
        # Check if subject contains important keywords
        if self._contains_important_keywords(email.subject):
            return True
        
        # Check if it's a recent email (last 30 days)
        if self._is_recent_email(email.date):
            return True
        
        # Check if it's a reply (contains Re: in subject)
        if email.subject.lower().startswith('re:'):
            return True
        
        # Filter out spam/marketing
        if self._is_spam(email):
            return False
        
        # Check email body for important content
        if self._contains_important_content(email.body):
            return True
        
        return False
    
    def _is_important_sender(self, sender: str) -> bool:
        sender_lower = sender.lower()
        return any(keyword.lower() in sender_lower for keyword in self.important_senders)
    
    def _contains_important_keywords(self, subject: str) -> bool:
        subject_lower = subject.lower()
        return any(keyword.lower() in subject_lower for keyword in self.important_subjects)
    
    def _is_recent_email(self, date: datetime) -> bool:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        return date > thirty_days_ago
    
    def _is_spam(self, email: EmailMessage) -> bool:
        # Check subject for spam keywords
        subject_lower = email.subject.lower()
        if any(keyword.lower() in subject_lower for keyword in self.spam_keywords):
            return True
        
        # Check sender for spam patterns
        sender_lower = email.sender.lower()
        if any(pattern in sender_lower for pattern in ['noreply', 'no-reply', 'marketing']):
            return True
        
        # Check if email has many recipients (likely marketing)
        # This would require additional parsing of headers
        
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