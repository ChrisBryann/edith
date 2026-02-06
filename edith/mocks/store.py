import json
import os
from typing import List, Dict, Any, Optional

class MockDataStore:
    def __init__(self, data_path: str = "edith/data/mock_store.json"):
        self.data_path = data_path
        self._data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Loads the JSON data from disk."""
        try:
            # Adjust path relative to where execution happens (usually root)
            abs_path = os.path.abspath(self.data_path)
            if not os.path.exists(abs_path):
                print(f"⚠️ Mock Data not found at {abs_path}")
                return {"accounts": {}, "knowledge_sources": {}}
                
            with open(abs_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading mock data: {e}")
            return {"accounts": {}, "knowledge_sources": {}}

    def get_emails(self, account_id: Optional[str] = None) -> List[Dict]:
        """Fetches emails, optionally filtered by account_id."""
        all_emails = []
        accounts = self._data.get("accounts", {})
        
        for acc_id, acc_data in accounts.items():
            if account_id and acc_id != account_id:
                continue
            
            emails = acc_data.get("emails", [])
            for email in emails:
                email["account_source"] = acc_id
                email["account_email"] = acc_data.get("email")
                all_emails.append(email)
                
        all_emails.sort(key=lambda x: x["date"], reverse=True)
        return all_emails

    def get_calendar_events(self, account_id: Optional[str] = None) -> List[Dict]:
        """Fetches calendar events, optionally filtered by account_id."""
        all_events = []
        accounts = self._data.get("accounts", {})
        
        for acc_id, acc_data in accounts.items():
            if account_id and acc_id != account_id:
                continue
                
            events = acc_data.get("calendar_events", [])
            for event in events:
                event["account_source"] = acc_id
                all_events.append(event)
                
        return all_events
