import asyncio
from datetime import datetime, timedelta, timezone
from typing import Set

from calendar_service import CalendarService

class NotificationService:
    def __init__(self, calendar_service: CalendarService):
        self.calendar_service = calendar_service
        self.notified_events: Set[str] = set()
        self.is_running = False
        
    async def start_monitoring(self, interval_seconds: int = 60):
        """Starts the background monitoring loop."""
        self.is_running = True
        print("🔔 Notification Service: Started monitoring for upcoming events.")
        
        while self.is_running:
            try:
                if self.calendar_service.service:
                    await self._check_upcoming_events()
            except Exception as e:
                print(f"Error in notification loop: {e}")
            
            await asyncio.sleep(interval_seconds)
            
    async def _check_upcoming_events(self):
        # Get events for the next 24 hours
        events = self.calendar_service.get_events(days_ahead=1)
        
        now = datetime.now(timezone.utc)
        reminder_window = timedelta(minutes=15)
        
        for event in events:
            # Ensure event time is timezone-aware for comparison
            if event.start_time.tzinfo is None:
                continue
                
            time_until_start = event.start_time - now
            
            # Check if event is within 15 minutes and hasn't been notified
            if timedelta(seconds=0) < time_until_start <= reminder_window:
                if event.id not in self.notified_events:
                    self._send_notification(f"🔔 Reminder: '{event.title}' starts in {int(time_until_start.total_seconds() / 60)} minutes.")
                    self.notified_events.add(event.id)

    def _send_notification(self, message: str):
        # In a real app, this would push to a WebSocket, Slack, or Mobile Push
        print(f"\n{message}\n")