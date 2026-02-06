from typing import List, Dict, Any
from edith.mocks.store import MockDataStore

class DummyCalendarService:
    def __init__(self):
        self.store = MockDataStore()
        print("📅 DummyCalendarService Initialized (Mock Data)")

    def authenticate(self):
        return True

    def get_events(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Fetches upcoming events from the mock store.
        Returns them in a format compatible with the RAG system / Frontend.
        """
        raw_events = self.store.get_calendar_events()
        
        # Simple string sort works for ISO format
        raw_events.sort(key=lambda x: x["start"])
        
        return raw_events
