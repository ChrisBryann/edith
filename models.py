from dataclasses import dataclass
from datetime import datetime
from enum import Enum

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