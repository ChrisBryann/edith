import pytest
import os
import shutil
from datetime import datetime, timedelta
from typing import List

from edith.config import EmailAssistantConfig
from edith.models import EmailMessage
from edith.services.email.rag import EmailRAGSystem
from tests.factories import get_dummy_data

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
def dummy_emails():
    return get_dummy_data()