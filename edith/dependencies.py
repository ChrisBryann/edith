from fastapi import Request
from edith.config import EmailAssistantConfig
from edith.services.email.fetcher import EmailFetcher
from edith.services.email.filter import EmailFilter
from edith.services.email.rag import EmailRAGSystem
from edith.services.calendar.service import CalendarService
from edith.services.notification.service import NotificationService
from edith.services.security.guard import PromptGuard

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

def get_rag_system(request: Request) -> EmailRAGSystem:
    return request.app.state.rag_system

def get_prompt_guard(request: Request) -> PromptGuard:
    return request.app.state.prompt_guard