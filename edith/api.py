import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Depends
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os

from edith.config import EmailAssistantConfig
from edith.lib.shared.models.calendar import CalendarEvent
from edith.lib.shared.models.email import EmailMessage
from edith.services.email.fetcher import EmailFetcher
from edith.mocks.email import DummyEmailFetcher
from edith.mocks.calendar import DummyCalendarService
from edith.services.calendar.service import CalendarService
from edith.services.notification.service import NotificationService
from edith.services.email.rag import EmailRAGSystem
from edith.services.email.filter.filter import EmailFilter
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
        # Initialize Fetcher based on configuration
        if app.state.config.use_mock_data:
            print("🎭 STARTING IN DEMO MODE (Mock Data)")
            app.state.email_fetcher = DummyEmailFetcher(app.state.config)
            app.state.calendar_service = DummyCalendarService()
        else:
            app.state.email_fetcher = EmailFetcher(app.state.config)
            app.state.calendar_service = CalendarService(app.state.config)

        # authenticate (only for real services)
        if not app.state.config.use_mock_data:
            if app.state.email_fetcher.authenticate():
                print("Email Service authenticated.")
        
        app.state.notification_service = NotificationService(app.state.calendar_service)
        
        # Initialize spam filter only if HF models are configured
        # This allows spam filtering in mock mode if desired, but gracefully skips if not configured
        if app.state.config.hf_token and app.state.config.spam_detection_model_id:
            try:
                app.state.email_filter = EmailFilter(app.state.config)
                print("📧 Spam filter initialized")
            except Exception as e:
                print(f"⚠️ Spam filter initialization failed: {e}")
                app.state.email_filter = None
        else:
            app.state.email_filter = None
            if not app.state.config.use_mock_data:
                print("⚠️ Spam filter disabled (HF_TOKEN or model IDs not configured)")
        
        app.state.prompt_guard = PromptGuard()
        
        # initialize RAG system
        if not app.state.config.gemini_api_key and not app.state.config.use_mock_data:
            raise Exception("Gemini API Key not configured!")
        
        app.state.rag_system = EmailRAGSystem(app.state.config)  # Initialized on startup
            
        if not app.state.config.use_mock_data and app.state.email_fetcher.creds:
            # Auto-configure primary email = app.state.email_fetcher.get_profile_email()
            user_email = app.state.email_fetcher.get_profile_email()
            app.state.config.add_email_account(user_email, is_primary=True)
            app.state.calendar_service.authenticate(app.state.email_fetcher.creds)
            print("Calendar authenticated.")
            notification_service_task = asyncio.create_task(app.state.notification_service.start_monitoring())
        yield
    except Exception as e:
        print(f"Startup authentication warning: {e}")
    finally:
        app.state.email_fetcher = None
        app.state.calendar_service = None
        app.state.notification_service = None
        app.state.email_filter = None
        app.state.rag_system = None
        app.state.prompt_guard = None
        print('Services has been shutdown.')
        if notification_service_task:
            notification_service_task.cancel()
        print('Notification monitoring service shutting down...')

app = FastAPI(
    title="Edith API",
    description="Backend API for Edith",
    version="0.1.0",
    lifespan=startup_event
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    sync_state: str = "idle" 
    sync_progress: int = 0
    sync_message: str = ""
    is_ready: bool = False

# --- Helper Functions ---
def format_calendar_events(events: List[dict]) -> str:
    if not events:
        return "No upcoming events found."
    lines = ["Upcoming Calendar Events:"]
    for event in events:
        # Handle both dict and CalendarEvent object (mock service returns dicts)
        title = event.get("summary") if isinstance(event, dict) else event.title
        start = event.get("start") if isinstance(event, dict) else event.start_time
        lines.append(f"- {title} at {start}")
    return "\n".join(lines)

# --- Endpoints ---
system_status = SystemStatus(is_authenticated=False)

@app.get("/system-status", response_model=SystemStatus)
async def get_system_status(email_fetcher: EmailFetcher = Depends(get_email_fetcher)):
    # In mock mode, we are technically "authenticated" enough
    system_status.is_authenticated = True if email_fetcher.config.use_mock_data else bool(email_fetcher.creds)
    return system_status

@app.get("/config-status")
async def get_config_status(config: EmailAssistantConfig = Depends(get_config)):
    return {
        "use_mock_data": config.use_mock_data,
        "env": config.env.value
    }

@app.post("/ask-question")
async def ask_question(request: QuestionRequest, rag_system: EmailRAGSystem = Depends(get_rag_system), calendar_service: CalendarService = Depends(get_calendar_service)):
    calendar_context = ""
    # In mock mode, we always get events
    events = calendar_service.get_events(days_ahead=7)
    if events:
        calendar_context = format_calendar_events(events)
    
    response = rag_system.answer_question(request.question, additional_context=calendar_context, return_sources=True)
    if isinstance(response, dict):
        return {
            "question": request.question, 
            "answer": response["answer"], 
            "sources": response.get("sources", [])
        }
    return {"question": request.question, "answer": response, "sources": []}

@app.get("/calendar-events")
async def get_calendar_events(days_ahead: int = 30, calendar_service: CalendarService = Depends(get_calendar_service)):
    # Check if it's the real service (which doesn't have 'store')
    if not hasattr(calendar_service, "store"):
         if not calendar_service.service:
             # Real service check
             raise HTTPException(status_code=401, detail="Calendar not authenticated")
    return calendar_service.get_events(days_ahead)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)