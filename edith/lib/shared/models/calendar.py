from datetime import datetime
from dataclasses import dataclass
@dataclass
class CalendarEvent:
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: str
    source_email: str
    calendar_type: str = "primary"