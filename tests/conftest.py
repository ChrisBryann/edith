import pytest
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict

from edith.config import EmailAssistantConfig
from edith.services.email.rag import EmailRAGSystem
from edith.services.email.filter.filter import EmailFilter
from tests.factories import get_dummy_data, get_dummy_live_data

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
def email_filter(test_config):
    """Initializes the Email Filter service"""
    if not test_config.spam_detection_model_id and not test_config.hf_token:
        pytest.skip("SPAM_DETECTION_MODEL_ID and/or HF_TOKEN not found in environment")
    
    filter = EmailFilter(test_config)
    
    return filter

@pytest.fixture(scope="session")
def dummy_emails():
    return get_dummy_data()

@pytest.fixture(scope="session")
def dummy_live_emails():
    return get_dummy_live_data()

@pytest.fixture(scope="session")
def dummy_single_email():
    return get_dummy_live_data(1)[0] # only one

@pytest.fixture(scope="session")
def record(metrics: Dict, expected_is_spam: bool, predicted_is_spam: bool):
    metrics["total"] += 1
    if expected_is_spam == predicted_is_spam:
        metrics["correct"] += 1
    else:
        if predicted_is_spam and not expected_is_spam:
            metrics["false_pos"] += 1
        elif not predicted_is_spam and expected_is_spam:
            metrics["false_neg"] += 1