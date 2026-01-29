from fastapi import Request
from config import EmailAssistantConfig
from services.email.fetcher import EmailFetcher
from services.email.filter import EmailFilter
from services.email.rag import EmailRAGSystem
from services.calendar.service import CalendarService
from services.notification.service import NotificationService

# --- Helper Functions ---
# Retrieves the required configs/services/utils to inject

def get_config(request: Request) -> EmailAssistantConfig:
    return request.app.state.config

def get_email_fetcher(request: Request) -> EmailFetcher:
    return request.app.state.email_fetcher

def get_email_filter(request: Request) -> EmailFilter:
    return request.app.state.email_filter

def get_calendar_service(request: Request) -> CalendarService:
    return request.app.state.calendar_service

def get_notification_service(request: Request) -> NotificationService:
    return request.app.state.notification_service

# def get_rag_system():
#     global rag_system
#     if rag_system is None:
#         if not config.gemini_api_key:
#             raise HTTPException(status_code=500, detail="Gemini API Key not configured")
#         rag_system = EmailRAGSystem(config)
#     return rag_system

def get_rag_system(request: Request) -> EmailRAGSystem:
    return request.app.state.rag_system