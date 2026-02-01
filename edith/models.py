from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from enum import Enum

@dataclass
class EmailConfig:
    email_address: str
    is_primary: bool = False
    account_type: str = "personal"  # personal, work, school

@dataclass
class EmailMessage:
    id: str
    subject: str
    sender: str
    body: str
    date: datetime
    is_relevant: bool = False
    account_type: str = "personal"
    labels: List[str] = field(default_factory=list)

@dataclass
class CalendarEvent:
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: str
    source_email: str
    calendar_type: str = "primary"

class Environment(Enum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"