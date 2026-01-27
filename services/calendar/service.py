from googleapiclient.discovery import build
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from models import CalendarEvent
from config import EmailAssistantConfig

class CalendarService:
    def __init__(self, config: EmailAssistantConfig):
        self.config = config
        self.service = None
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        
    def authenticate(self, creds) -> bool:
        """Authenticate with Google Calendar using existing credentials"""
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            return True
        except Exception as e:
            print(f"Error authenticating with Calendar: {e}")
            return False
    
    def get_events(self, days_ahead: int = 30) -> List[CalendarEvent]:
        """Get events from the primary calendar"""
        if not self.service:
            raise Exception("Not authenticated")
        
        try:
            # Calculate time range
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            end_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            # Get primary calendar events
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            calendar_events = []
            for event in events:
                calendar_event = self._parse_event(event)
                if calendar_event:
                    calendar_events.append(calendar_event)
            
            return calendar_events
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []
    
    def get_all_calendar_events(self, days_ahead: int = 30) -> List[CalendarEvent]:
        """Get events from all accessible calendars"""
        if not self.service:
            raise Exception("Not authenticated")
        
        all_events = []
        
        try:
            # Get list of calendars
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            
            for calendar in calendars:
                if calendar['accessRole'] in ['owner', 'writer', 'reader']:
                    events = self._get_calendar_events(calendar['id'], days_ahead)
                    all_events.extend(events)
            
            # Sort events by start time
            all_events.sort(key=lambda x: x.start_time)
            return all_events
            
        except Exception as e:
            print(f"Error fetching all calendar events: {e}")
            return []
    
    def _get_calendar_events(self, calendar_id: str, days_ahead: int) -> List[CalendarEvent]:
        """Get events from a specific calendar"""
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            end_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            calendar_events = []
            
            for event in events:
                calendar_event = self._parse_event(event, calendar_id)
                if calendar_event:
                    calendar_events.append(calendar_event)
            
            return calendar_events
            
        except Exception as e:
            print(f"Error fetching events from calendar {calendar_id}: {e}")
            return []
    
    def _parse_event(self, event: Dict[str, Any], calendar_id: str = 'primary') -> Optional[CalendarEvent]:
        """Parse a calendar event from Google Calendar API response"""
        try:
            title = event.get('summary', 'No Title')
            description = event.get('description', '')
            
            # Parse start and end times
            start = event.get('start', {})
            end = event.get('end', {})
            
            if 'dateTime' in start:
                # This is a timed event
                start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
            else:
                # This is an all-day event
                start_time = datetime.fromisoformat(start['date'])
                end_time = datetime.fromisoformat(end['date'])
                # Add one day to end_time for all-day events
                end_time = end_time + timedelta(days=1)
            
            primary_email = self.config.get_primary_email()
            if primary_email is None:
                return None
                
            return CalendarEvent(
                id=event['id'],
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
                source_email=primary_email,
                calendar_type=calendar_id
            )
        except Exception as e:
            print(f"Error parsing event: {e}")
            return None
    
    def create_unified_event(self, calendar_event: CalendarEvent) -> bool:
        """Create a unified event in the primary calendar"""
        if not self.service:
            raise Exception("Not authenticated")
        
        try:
            event_body = {
                'summary': f"[{calendar_event.source_email}] {calendar_event.title}",
                'description': calendar_event.description,
                'start': {
                    'dateTime': calendar_event.start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': calendar_event.end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event_body
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error creating unified event: {e}")
            return False