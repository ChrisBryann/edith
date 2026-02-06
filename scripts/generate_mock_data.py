import json
import os
import datetime
from pathlib import Path
from typing import Dict, List, Any

# ISO Format helper
def get_time(day_offset: int, hour: int, minute: int) -> str:
    """Returns an ISO timestamp relative to today."""
    now = datetime.datetime.now()
    target = now + datetime.timedelta(days=day_offset)
    target = target.replace(hour=hour, minute=minute, second=0, microsecond=0)
    # Adding a dummy timezone offset for realism (-08:00 PST)
    return target.isoformat() + "-08:00"

# --- Generators for each Source ---

def generate_work_account() -> Dict[str, Any]:
    """Mocks a corporate Google Workspace account."""
    return {
        "type": "google_workspace",
        "email": "alex@techflow.com",
        "calendar_events": [
            {
                "summary": "Project Phoenix Launch - Go/No-Go",
                "start": get_time(0, 14, 0), # Today 2 PM
                "end": get_time(0, 15, 0),
                "description": "Final review before release. Attendance mandatory.",
                "location": "Boardroom A / Zoom"
            },
            {
                "summary": "Weekly All-Hands",
                "start": get_time(0, 10, 0), # Today 10 AM
                "end": get_time(0, 11, 0),
                "description": "Updates from all departments."
            },
            {
                 "summary": "Q4 Strategy Sync",
                 "start": get_time(1, 11, 0), # Tomorrow 11 AM
                 "end": get_time(1, 12, 0)
            }
        ],
        "emails": [
            {
                "id": "work_101",
                "subject": "Prep for Launch Meeting later?",
                "sender": "sarah.chen@techflow.com",
                "snippet": "Hey Alex, are we ready for the 2pm Go/No-Go?",
                "body": "Hey Alex,\n\nAre we ready for the 2pm Go/No-Go? I'm still waiting on the QA sign-off from Dave. If we don't get it by noon, we might need to delay.\n\nLet me know,\nSarah",
                "date": get_time(0, 9, 15),
                "labels": ["INBOX", "IMPORTANT"]
            },
            {
                "id": "work_102",
                "subject": "RE: QA Sign-off",
                "sender": "dave.miller@techflow.com",
                "snippet": "Apologies for the delay. The build passed all integration tests.",
                "body": "Sarah/Alex,\n\nApologies for the delay. The build passed all integration tests. You have my GREEN light for the launch.\n\nSee you at the all-hands.\n\n- Dave",
                "date": get_time(0, 9, 45),
                "labels": ["INBOX"]
            },
             {
                "id": "work_103",
                "subject": "Quick Q",
                "sender": "intern@techflow.com",
                "snippet": "where did we store the logo assets?",
                "body": "hi alex,\n\nsorry to bother u, but i cant find the phoenix logo assets. serveer seems down??\n\nthx\nj.",
                "date": get_time(0, 11, 30),
                "labels": ["INBOX"]
            }
        ]
    }

def generate_personal_account() -> Dict[str, Any]:
    """Mocks a personal Gmail account."""
    return {
        "type": "gmail",
        "email": "alex.doe@gmail.com",
        "calendar_events": [
            {
                "summary": "Dentist Appointment",
                "start": get_time(0, 16, 30), # Today 4:30 PM
                "end": get_time(0, 17, 30),
                "location": "Dr. Smith's Office"
            },
            {
                "summary": "Gym Session",
                "start": get_time(0, 18, 0), # Today 6:00 PM
                "end": get_time(0, 19, 0)
            }
        ],
        "emails": [
            {
                "id": "pers_201",
                "subject": "Appointment Reminder: 4:30 PM Today",
                "sender": "noreply@drsmithdental.com",
                "snippet": "This is a reminder for your appointment with Dr. Smith today.",
                "body": "Dear Alex,\n\nSee you today at 4:30 PM. Please arrive 10 minutes early.\n\nRegards,\nFront Desk",
                "date": get_time(0, 8, 0),
                "labels": ["INBOX", "UPDATES"]
            },
            {
                "id": "pers_202",
                "subject": "Dinner tonight?",
                "sender": "jessica.doe@gmail.com",
                "snippet": "Are we still on for sushi after your gym?",
                "body": "Hey,\n\nAre we still on for sushi after your gym session? I can book a table for 7:30.\n\nLet me know!",
                "date": get_time(0, 12, 0),
                "labels": ["INBOX"]
            }
        ]
    }

def generate_mcp_docs() -> Dict[str, Any]:
    """Mocks an MCP server providing documentation."""
    return {
        "type": "mcp_resource",
        "name": "Project Phoenix Documentation",
        "items": [
            {
                "title": "Architecture Overview",
                "content": "Project Phoenix is a microservices-based platform designed to replace the legacy monolith 'Icarus'. It uses Kubernetes, Istio, and gRPC for inter-service communication."
            },
            {
                "title": "Deployment Strategy",
                "content": "We are using a Blue/Green deployment strategy. The 'Green' environment is currently staged on the 'us-west-2' cluster."
            }
        ]
    }

def generate_meeting_transcripts() -> Dict[str, Any]:
    """Mocks a transcript source (e.g. from a call recorder)."""
    return {
        "type": "transcript_store",
        "name": "Meeting Transcripts",
        "items": [
            {
                "title": "Sync with Design Team",
                "date": get_time(-1, 14, 0),
                "content": "ALEX: We need the dark mode assets by Friday.\nDESIGN: We are finalizing the palette now. The purple accent is approved."
            }
        ]
    }

def main():
    import sys
    # Force UTF-8 encoding for console output
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            # Python < 3.7 or special environments
            pass

    print("🚀 Generating Mock Data...")
    
    data = {
        "generated_at": datetime.datetime.now().isoformat(),
        "accounts": {
            "work_main": generate_work_account(),
            "personal": generate_personal_account()
        },
        "knowledge_sources": {
            "project_phoenix_docs": generate_mcp_docs(),
            "recent_calls": generate_meeting_transcripts()
        }
    }
    
    # Ensure directory exists
    output_dir = Path("edith/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "mock_store.json"
    
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"✅ Mock data generated at: {output_file.absolute()}")

if __name__ == "__main__":
    main()
