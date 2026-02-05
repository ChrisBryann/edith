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
    is_unread: bool
    headers: Dict[str, str]   # e.g. {"List-Unsubscribe": "..."}
    is_relevant: bool = False
    account_type: str = "personal"
    labels: List[str] = field(default_factory=list)