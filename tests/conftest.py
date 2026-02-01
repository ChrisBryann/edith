import pytest
import os
import shutil
from datetime import datetime, timedelta
from typing import List

from config import EmailAssistantConfig
from lib.shared.models.email import EmailMessage
from services.email.rag import EmailRAGSystem
from lib.shared.llm.spam_service import SpamLLMService

@pytest.fixture(scope="session")
def test_config():
    """Sets up the test configuration and cleans up DB after tests."""
    # Force Test Environment
    os.environ["EDITH_ENV"] = "test"
    config = EmailAssistantConfig()
    
    # Pre-test cleanup
    if os.path.exists(config.chroma_db_path):
        shutil.rmtree(config.chroma_db_path)
        
    yield config
    
    # Post-test cleanup
    if os.path.exists(config.chroma_db_path):
        shutil.rmtree(config.chroma_db_path)

@pytest.fixture(scope="session")
def rag_system(test_config):
    """Initializes the RAG system and indexes dummy data once for all tests."""
    if not test_config.gemini_api_key:
        pytest.skip("GEMINI_API_KEY not found in environment")

    rag = EmailRAGSystem(test_config)
    
    # Index Dummy Data
    emails = get_dummy_data()
    rag.index_emails(emails)
    
    return rag

@pytest.fixture(scope="session")
def spam_llm_service(test_config):
    """Initializes the Spam Detection LLM service"""
    if not test_config.spam_detection_model_id:
        pytest.skip("SPAM_DETECTION_MODEL_ID not found in environment")
    
    service = SpamLLMService(test_config)
    
    return service

@pytest.fixture(scope="session")
def dummy_emails():
    return get_dummy_data()

def get_dummy_data() -> List[EmailMessage]:
    """Generates a diverse set of dummy emails for testing RAG."""
    base_date = datetime.now()
    
    return [
        # Scenario 1: Work Project Deadline
        EmailMessage(
            id="work_1",
            subject="Project Phoenix Deadline Update",
            sender="manager@techcorp.com",
            body="Team, just a reminder that the Project Phoenix deadline has been moved to next Friday, November 15th. We need the final report by Wednesday.",
            date=base_date - timedelta(days=2),
            is_relevant=True,
            account_type="work"
        ),
        # Scenario 2: Technical Details
        EmailMessage(
            id="work_2",
            subject="Phoenix API Specs",
            sender="lead@techcorp.com",
            body="For the Phoenix API, we are using port 8080 for the staging environment and port 3000 for dev. The API key for staging is STAGING_KEY_99.",
            date=base_date - timedelta(days=1),
            is_relevant=True,
            account_type="work"
        ),
        # Scenario 3: Personal Event
        EmailMessage(
            id="personal_1",
            subject="Mom's Surprise Party",
            sender="sister@family.com",
            body="We are hosting Mom's 60th birthday at The Italian Place on Main St. It's this Saturday at 7 PM. Don't forget to bring the photo album!",
            date=base_date - timedelta(days=3),
            is_relevant=True,
            account_type="personal"
        ),
        # Scenario 4: Travel
        EmailMessage(
            id="travel_1",
            subject="Flight Confirmation: NYC to Tokyo",
            sender="bookings@airline.com",
            body="Your flight JL005 departs from JFK Terminal 1 on Dec 20th at 12:30 PM. Seat 14A confirmed.",
            date=base_date - timedelta(days=5),
            is_relevant=True,
            account_type="personal"
        ),
        # Scenario 5: Irrelevant Email (Should be skipped by RAG if is_relevant=False)
        EmailMessage(
            id="spam_1",
            subject="Win a free iPhone!",
            sender="promo@spam.com",
            body="Click here to claim your prize now!",
            date=base_date,
            is_relevant=False,
            account_type="personal"
        )
    ]