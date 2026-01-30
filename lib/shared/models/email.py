from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class EmailConfig:
    email_address: str
    is_primary: bool = False
    account_type: str = "personal"  # personal, work, school

@dataclass
class EmailMessage:
    id: str
    thread_id: Optional[str]
    sender: str # from email
    to_emails: List[str]
    cc_emails: List[str]
    subject: str
    body: str
    date: datetime
    is_relevant: bool = False
    is_unread: bool
    account_type: str = "personal"
    has_attachments: bool
    labels: List[str] = field(default_factory=list)
    headers: Dict[str, str]   # e.g. {"List-Unsubscribe": "..."}

@dataclass
class EmailFilterScore:
    email_id: str
    score: float
    bucket: str
    reasons: list[str] = field(default_factory=list)