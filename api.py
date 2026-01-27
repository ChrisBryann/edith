import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

# Add the current directory to Python path to ensure modules can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import EmailAssistantConfig
from models import CalendarEvent
from services.email.fetcher import EmailFetcher
from services.calendar.service import CalendarService
from services.notification.service import NotificationService
from services.email.rag import EmailRAGSystem
from services.email.filter import EmailFilter

app = FastAPI(
    title="Edith API",
    description="Backend API for Edith Email Assistant",
    version="0.1.0"
)

# --- Global Services ---
config = EmailAssistantConfig()
email_fetcher = EmailFetcher(config)
calendar_service = CalendarService(config)
notification_service = NotificationService(calendar_service)
email_filter = EmailFilter()
rag_system = None  # Initialized on startup

# --- Pydantic Models ---
class EmailAccountRequest(BaseModel):
    email_address: str
    is_primary: bool = False
    account_type: str = "personal"

class QuestionRequest(BaseModel):
    question: str

# --- Helper Functions ---
def get_rag_system():
    global rag_system
    if rag_system is None:
        if not config.gemini_api_key:
            raise HTTPException(status_code=500, detail="Gemini API Key not configured")
        rag_system = EmailRAGSystem(config)
    return rag_system

def format_calendar_events(events: List[CalendarEvent]) -> str:
    if not events:
        return "No upcoming events found."
    lines = ["Upcoming Calendar Events:"]
    for event in events:
        lines.append(f"- {event.title} at {event.start_time} (ID: {event.id})")
    return "\n".join(lines)

# --- Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    # Ensure directories exist
    os.makedirs(config.chroma_db_path, exist_ok=True)
    
    # Attempt authentication
    try:
        if email_fetcher.authenticate():
            print("Gmail authenticated.")
            
            # Auto-configure primary email
            user_email = email_fetcher.get_profile_email()
            config.add_email_account(user_email, is_primary=True)
            
            # Share credentials with Calendar Service
            if email_fetcher.creds:
                calendar_service.authenticate(email_fetcher.creds)
                print("Calendar authenticated.")
                
                # Start background notification service
                asyncio.create_task(notification_service.start_monitoring())
    except Exception as e:
        print(f"Startup authentication warning: {e}")

# --- Endpoints ---

@app.post("/add-email-account")
async def add_email_account(account: EmailAccountRequest):
    config.add_email_account(
        account.email_address, 
        account.is_primary, 
        account.account_type
    )
    return {"status": "success", "message": f"Added {account.email_address}"}

@app.post("/sync-emails")
async def sync_emails(background_tasks: BackgroundTasks):
    if not email_fetcher.creds: # Check auth status
        raise HTTPException(status_code=401, detail="Service not authenticated")

    def process_sync():
        print("Starting background sync...")
        emails = email_fetcher.get_emails(max_results=50)
        relevant = email_filter.filter_relevant_emails(emails)
        if relevant:
            system = get_rag_system()
            system.index_emails(relevant)
        print(f"Synced {len(relevant)} relevant emails out of {len(emails)} fetched.")

    background_tasks.add_task(process_sync)
    return {"status": "success", "message": "Sync started in background"}

@app.post("/ask-question")
async def ask_question(request: QuestionRequest):
    system = get_rag_system()
    
    # Fetch calendar context to enrich the answer
    calendar_context = ""
    if calendar_service.service:
        events = calendar_service.get_events(days_ahead=7)
        calendar_context = format_calendar_events(events)
    
    answer = system.answer_question(request.question, additional_context=calendar_context)
    return {"question": request.question, "answer": answer}

@app.get("/email-summary")
async def email_summary(days: int = 7):
    system = get_rag_system()
    summary = system.get_email_summary(days=days)
    return {"days": days, "summary": summary}

@app.get("/calendar-events")
async def get_calendar_events(days_ahead: int = 30):
    if not calendar_service.service:
        raise HTTPException(status_code=401, detail="Calendar not authenticated")
    return calendar_service.get_events(days_ahead)

@app.get("/relevant-emails")
async def get_relevant_emails(limit: int = 20):
    if not email_fetcher.creds:
        raise HTTPException(status_code=401, detail="Service not authenticated")
    emails = email_fetcher.get_emails(max_results=limit*2)
    relevant = email_filter.filter_relevant_emails(emails)
    return relevant[:limit]

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe an uploaded audio file (MP3, WAV, etc.)"""
    system = get_rag_system()
    
    # Read file content
    content = await file.read()
    transcript = system.transcribe_audio(content, mime_type=file.content_type or "audio/mp3")
    
    return {"filename": file.filename, "transcript": transcript}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)