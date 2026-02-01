from fastapi import Request
from .gmail import GmailService

# --- Helper Functions for Providers ---

def get_gmail_service(request: Request) -> GmailService:
    return request.app.state.gmail_service