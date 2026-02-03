import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Depends
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os

from edith.config import EmailAssistantConfig
from edith.models import CalendarEvent
from edith.services.email.fetcher import EmailFetcher
from edith.services.calendar.service import CalendarService
from edith.services.notification.service import NotificationService
from edith.services.email.rag import EmailRAGSystem
from edith.services.email.filter import EmailFilter
from edith.services.security.guard import PromptGuard

from edith.dependencies import *


# --- Lifecycle Events ---
@asynccontextmanager
async def startup_event(app: FastAPI):
    
    # Ensure configurations are initialized
    app.state.config = EmailAssistantConfig()
    
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
        app.state.prompt_guard = PromptGuard()
        
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
        app.state.prompt_guard = None
        
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

# --- Pydantic Models ---
class EmailAccountRequest(BaseModel):
    email_address: str
    is_primary: bool = False
    account_type: str = "personal"

class QuestionRequest(BaseModel):
    question: str

class SystemStatus(BaseModel):
    is_authenticated: bool
    sync_state: str = "idle"  # idle, syncing, completed, error
    sync_progress: int = 0
    sync_message: str = ""
    is_ready: bool = False

# --- Helper Functions ---

def format_calendar_events(events: List[CalendarEvent]) -> str:
    if not events:
        return "No upcoming events found."
    lines = ["Upcoming Calendar Events:"]
    for event in events:
        lines.append(f"- {event.title} at {event.start_time} (ID: {event.id})")
    return "\n".join(lines)

# --- Endpoints ---

# Global Status State
system_status = SystemStatus(is_authenticated=False)

@app.get("/system-status", response_model=SystemStatus)
async def get_system_status(email_fetcher: EmailFetcher = Depends(get_email_fetcher)):
    # Update auth status dynamically
    system_status.is_authenticated = bool(email_fetcher.creds)
    return system_status

@app.post("/add-email-account")
async def add_email_account(account: EmailAccountRequest, config: EmailAssistantConfig = Depends(get_config)):
    config.add_email_account(
        account.email_address, 
        account.is_primary, 
        account.account_type
    )
    return {"status": "success", "message": f"Added {account.email_address}"}

@app.post("/sync-emails")
async def sync_emails(background_tasks: BackgroundTasks, email_fetcher: EmailFetcher = Depends(get_email_fetcher), email_filter: EmailFilter = Depends(get_email_filter), rag_system: EmailRAGSystem = Depends(get_rag_system), prompt_guard: PromptGuard = Depends(get_prompt_guard)):
    if not email_fetcher.creds: # Check auth status
        raise HTTPException(status_code=401, detail="Service not authenticated")

    def process_sync():
        print("Starting background sync...")
        system_status.sync_state = "syncing"
        system_status.sync_progress = 0
        system_status.sync_message = "Starting sync..."
        
        page_token = None
        total_fetched = 0
        
        # Target: 1 month back
        # Optimization: Filter out noise (Promotions, Social, Spam) at the provider level
        query = "newer_than:1m -category:promotions -category:social -in:spam -in:trash"
        # Readiness threshold: 7 days back
        readiness_date = datetime.now() - timedelta(days=7)
        # Hard cap to prevent long sync times during demo
        MAX_EMAILS = 500
        
        try:
            while True:
                if total_fetched >= MAX_EMAILS:
                    break

                # Fetch batch
                emails, next_token = email_fetcher.get_emails(max_results=50, query=query, page_token=page_token)
                if not emails:
                    break
                
                # Zero Trust Ingestion: Filter unsafe content immediately
                safe_emails = []
                for email in emails:
                    if prompt_guard.validate(email.subject + " " + email.body):
                        safe_emails.append(email)
                    else:
                        print(f"   🛡️ Security Alert: Dropped email '{email.subject[:30]}...' at ingestion.")
                
                total_fetched += len(safe_emails)
                system_status.sync_message = f"Fetched {total_fetched} emails..."
                
                relevant = email_filter.filter_relevant_emails(safe_emails)
                if relevant:
                    rag_system.index_emails(relevant)
                    
                system_status.sync_progress = total_fetched
                
                # Check readiness (if we have processed emails older than readiness threshold)
                if not system_status.is_ready and emails:
                    # Gmail returns newest first. Check the oldest in this batch.
                    oldest_date = min(e.date for e in emails)
                    # Make offset-naive for comparison to avoid timezone headaches
                    if oldest_date.tzinfo is not None:
                        oldest_date = oldest_date.replace(tzinfo=None)
                    
                    if oldest_date < readiness_date:
                        system_status.is_ready = True
                
                page_token = next_token
                if not page_token:
                    break
            
            system_status.sync_state = "completed"
            system_status.sync_message = f"Sync complete. Processed {total_fetched} emails."
            system_status.is_ready = True
            print(f"Sync complete. Total fetched: {total_fetched}")
            
        except Exception as e:
            print(f"Sync error: {e}")
            system_status.sync_state = "error"
            system_status.sync_message = f"Error: {str(e)}"

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
    emails, _ = email_fetcher.get_emails(max_results=limit*2)
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