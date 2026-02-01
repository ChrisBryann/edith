import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Depends
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from services.email.routers import email_app
import os

from config import EmailAssistantConfig
from models import CalendarEvent
from services.email.fetcher import EmailFetcher
from services.calendar.service import CalendarService
from services.notification.service import NotificationService
from services.email.rag import EmailRAGSystem
from services.email.filter import EmailFilter

from helpers import *


# --- Lifecycle Events ---
@asynccontextmanager
async def startup_event(app: FastAPI):
    
    # Ensure configurations are initialized
    # Create a unique ID for user when startup (temporary sol, in future we use local DB)
    app.state.config = EmailAssistantConfig(user_id=uuid4().hex)
    
    # Ensure directories exist
    os.makedirs(app.state.config.chroma_db_path, exist_ok=True)
    notification_service_task = None
    # Attempt authentication
    try:
        # --- Global Services ---
        app.state.email_fetcher = EmailFetcher(app.state.config)
        app.state.calendar_service = CalendarService(app.state.config)
        app.state.notification_service = NotificationService(app.state.calendar_service)
        app.state.email_filter = EmailFilter()
        
        # initialize RAG system - check if Gemini API Key is defined from env
        if not app.state.config.gemini_api_key:
            raise Exception("Gemini API Key not configured!")
        
        app.state.rag_system = EmailRAGSystem(app.state.config)  # Initialized on startup
        
        if app.state.email_fetcher.authenticate():
            print("Gmail authenticated.")
            
            # Auto-configure primary email
            user_email = app.state.email_fetcher.get_profile_email()
            app.state.config.add_email_account(user_email, is_primary=True)
            
            # Share credentials with Calendar Service
            if app.state.email_fetcher.creds:
                app.state.calendar_service.authenticate(app.state.email_fetcher.creds)
                print("Calendar authenticated.")
                
                # Start background notification service
                notification_service_task = asyncio.create_task(app.state.notification_service.start_monitoring())
            yield
    except Exception as e:
        print(f"Startup authentication warning: {e}")
    finally:
        # Shutdown services and any background tasks
        app.state.email_fetcher = None
        app.state.calendar_service = None
        app.state.notification_service = None
        app.state.email_filter = None
        app.state.rag_system = None
        
        print('Services has been shutdown.')
        
        notification_service_task.cancel()
        print('Notification monitoring service shutting down...')
        
        try:
            await notification_service_task
        except asyncio.CancelledError:
            print("Notification monitoring service has been shutdown.")
        


app = FastAPI(
    title="Edith API",
    description="Backend API for Edith Email Assistant",
    version="0.1.0",
    lifespan=startup_event
)

# Include email subrouter
app.mount('/email', email_app)

# --- Pydantic Models ---
class EmailAccountRequest(BaseModel):
    email_address: str
    is_primary: bool = False
    account_type: str = "personal"

class QuestionRequest(BaseModel):
    question: str

# --- Helper Functions ---

def format_calendar_events(events: List[CalendarEvent]) -> str:
    if not events:
        return "No upcoming events found."
    lines = ["Upcoming Calendar Events:"]
    for event in events:
        lines.append(f"- {event.title} at {event.start_time} (ID: {event.id})")
    return "\n".join(lines)

# --- Endpoints ---

@app.post("/add-email-account")
async def add_email_account(account: EmailAccountRequest, config: EmailAssistantConfig = Depends(get_config)):
    config.add_email_account(
        account.email_address, 
        account.is_primary, 
        account.account_type
    )
    return {"status": "success", "message": f"Added {account.email_address}"}

@app.post("/sync-emails")
async def sync_emails(background_tasks: BackgroundTasks, email_fetcher: EmailFetcher = Depends(get_email_fetcher), email_filter: EmailFilter = Depends(get_email_filter), rag_system: EmailRAGSystem = Depends(get_rag_system)):
    if not email_fetcher.creds: # Check auth status
        raise HTTPException(status_code=401, detail="Service not authenticated")

    def process_sync():
        print("Starting background sync...")
        emails = email_fetcher.get_emails(max_results=50)
        relevant = email_filter.filter_relevant_emails(emails)
        if relevant:
            rag_system.index_emails(relevant)
        print(f"Synced {len(relevant)} relevant emails out of {len(emails)} fetched.")

    background_tasks.add_task(process_sync)
    return {"status": "success", "message": "Sync started in background"}

@app.post("/ask-question")
async def ask_question(request: QuestionRequest, rag_system: EmailRAGSystem = Depends(get_rag_system), calendar_service: CalendarService = Depends(get_calendar_service)):
    
    # Fetch calendar context to enrich the answer
    calendar_context = ""
    if calendar_service.service:
        events = calendar_service.get_events(days_ahead=7)
        calendar_context = format_calendar_events(events)
    
    answer = rag_system.answer_question(request.question, additional_context=calendar_context)
    return {"question": request.question, "answer": answer}

@app.get("/email-summary")
async def email_summary(days: int = 7, rag_system: EmailRAGSystem = Depends(get_rag_system)):
    summary = rag_system.get_email_summary(days=days)
    return {"days": days, "summary": summary}

@app.get("/calendar-events")
async def get_calendar_events(days_ahead: int = 30, calendar_service: CalendarService = Depends(get_calendar_service)):
    if not calendar_service.service:
        raise HTTPException(status_code=401, detail="Calendar not authenticated")
    return calendar_service.get_events(days_ahead)

@app.get("/relevant-emails")
async def get_relevant_emails(limit: int = 20, email_fetcher: EmailFetcher = Depends(get_email_fetcher), email_filter: EmailFilter = Depends(get_email_filter)):
    if not email_fetcher.creds:
        raise HTTPException(status_code=401, detail="Service not authenticated")
    emails = email_fetcher.get_emails(max_results=limit*2)
    relevant = email_filter.filter_relevant_emails(emails)
    return relevant[:limit]

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), rag_system: EmailRAGSystem = Depends(get_rag_system)):
    """Transcribe an uploaded audio file (MP3, WAV, etc.)"""
    
    # Read file content
    content = await file.read()
    transcript = rag_system.transcribe_audio(content, mime_type=file.content_type or "audio/mp3")
    
    return {"filename": file.filename, "transcript": transcript}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)