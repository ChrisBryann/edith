import re
import logging
from typing import List
from datetime import datetime, timedelta

from .constants import SPAM_KEYWORDS, IMPORTANT_SENDERS, IMPORTANT_SUBJECTS, LIST_HEADER_KEYS, ZERO_SHOT_SPAM_LABELS

from edith.lib.shared.models import EmailMessage, EmailFilterScore
from edith.config import EmailAssistantConfig
from edith.lib.shared.llm.spam_service import SpamLLMService

logger = logging.getLogger(__name__)

class EmailFilter:
    def __init__(self, config: EmailAssistantConfig):
        self.spam_service = SpamLLMService(config)
        
    def filter_relevant_emails(self, emails: List[EmailMessage], user_primary_email: str) -> List[EmailMessage]:
        relevant_emails = []
        
        for email in emails:
            if not self._is_spam_ml(email):
                email.is_relevant = True
                relevant_emails.append(email)
        
        
        
        # for email in emails:
        #     score = self.score_email(email, now=datetime.now(), user_email=user_primary_email, vip_senders=IMPORTANT_SENDERS, known_senders={})
        #     if score.bucket != 'other':
        #         email.is_relevant = True
        #         relevant_emails.append(email)    
        
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
    
    def score_email(
        self,
        email: EmailMessage,
        *,
        now: datetime,
        user_email: str,
        vip_senders: set[str] = frozenset(),
        known_senders: set[str] = frozenset() # optional: from address book/history
        ) -> EmailFilterScore:
        
        reasons = []
        score = 0.0
        
        # VIP sender
        if email.sender.lower() in {s.lower() for s in vip_senders}:
            score += 0.35
            reasons.append("From a VIP sender")
            
        # Directness: sent to user (not huge recipient list)
        direct_to_user = user_email.lower() in {e.lower() for e in email.to_emails}
        many_recipients = len(email.to_emails) + len(email.cc_emails) >= 6 # TODO: this value can change
        if direct_to_user and not many_recipients:
            score += 0.20
            reasons.append("Directly addressed to you")
         # Unread
        if email.is_unread:
            score += 0.10
            reasons.append("Unread")

        # Recency
        r = self._recency_score(email.received_at, now)
        score += 0.15 * r
        if r >= 0.8:
            reasons.append("Recent")

        # Keywords
        text = f"{email.subject}\n{email.snippet}\n{email.body_text or ''}"
        if self._contains_any_keyword(text, IMPORTANT_SUBJECTS):
            score += 0.20
            reasons.append("Contains important keywords")

        # Known sender (optional) -> important senders
        if email.sender.lower() in {s.lower() for s in known_senders}:
            score += 0.10
            reasons.append("Known sender")

        # Negative signals
        if self._is_mailing_list(email.headers):
            score -= 0.25
            reasons.append("Looks like a mailing list/newsletter")

        # Filter out explicit Promotions and Social categories
        if (email.labels and 'CATEGORY_PROMOTIONS' in email.labels or 'CATEGORY_SOCIAL' in email.labels):
            score -= 0.10
            reasons.append("Looks promotional")

        score = self._clamp01(score)
        
        # If Spam, rule it out TODO: should I immediately zero it out?
        if self._contains_any_keyword(text, SPAM_KEYWORDS):
            score = 0.0

        # Additional, get the prediction score from ML Spam Detection using TinyBERT
        ml_results = self.spam_service.detect_spam([f'Subject: {email.subject}\n\n{email.body}'])
        ml_score = 0.0
        if ml_results:
            if ml_results[0].label == 'No spam':
                ml_score = ml_results[0].score
            
            score = (score + (1 - ml_score)) / 2
            
            
            
        # Bucket thresholds TODO: (tune these)
        # if score >= 0.75:
        #     bucket = "important"
        # elif score >= 0.45:
        #     bucket = "relevant"
        # else:
        #     bucket = "other"
            

        # return EmailFilterScore(email_id=email.id, score=score, bucket=bucket, reasons=reasons)
        
        return score >= 0.75
    
    
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
    
    def _is_mailing_list(headers: dict) -> bool:
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
    
    def _recency_score(received_at: datetime, now: datetime) -> float:
        age = now - received_at
        if age <= timedelta(hours=6): return 1.0
        if age <= timedelta(days=1): return 0.8
        if age <= timedelta(days=3): return 0.6
        if age <= timedelta(days=7): return 0.4
        return 0.2
    
    def _clamp01(x: float) -> float:
        return 0.0 if x < 0 else 1.0 if x > 1 else x
    
    def _contains_any_keyword(text: str, keywords: set[str]) -> bool:
        t = (text or "").lower()
        return any(k.lower() in t for k in keywords)