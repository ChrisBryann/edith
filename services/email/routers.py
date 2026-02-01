from fastapi import FastAPI, Depends, status, Response
from contextlib import asynccontextmanager
from providers.gmail import GmailService
from providers.helpers import get_gmail_service
from helpers import get_config
from config import EmailAssistantConfig
from pydantic import BaseModel
from typing import Optional

@asynccontextmanager
def on_startup(app: FastAPI):
    try:
        app.state.gmail_service = GmailService(app.state.config)
        yield
    except Exception as e:
        print(f'Email subrouter startup failed: {e}')
    finally:
        app.state.gmail_service = None
        print('Email subrouter has shutdown')

email_app = FastAPI(lifespan=on_startup)

class ConnectGmailRequest:
    token_filename: Optional[str]

@email_app.post('/connect/gmail')
def connect_gmail_account(connect_gmail_request: ConnectGmailRequest, gmail_service: GmailService = Depends(get_gmail_service), config: EmailAssistantConfig = Depends(get_config)):
    # Authorize app to access user's Gmail account through Gmail API
    gmail_service.authenticate(connect_gmail_request.token_filename)
