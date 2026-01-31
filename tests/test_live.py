import pytest
import os
from services.email.fetcher import EmailFetcher
from services.email.filter import EmailFilter
from services.email.rag import EmailRAGSystem

@pytest.mark.integration
def test_live_gmail_integration(test_config):
    """
    Integration test that connects to real Gmail.
    
    Prerequisites:
    1. 'credentials.json' must exist in root.
    2. 'token.json' must exist (authenticated locally via main.py).
    """
    # 1. Setup & Checks
    if not os.path.exists(test_config.gmail_credentials_path):
        pytest.skip("Skipping live test: credentials.json not found")
    
    # Check for token.json to avoid interactive auth prompt hanging the test
    if not os.path.exists("token.json"):
         pytest.skip("Skipping live test: token.json not found. Run 'python main.py' to authenticate first.")

    # Force mock data OFF for this test to ensure we hit real Gmail
    test_config.use_mock_data = False

    # 2. Initialize Fetcher
    fetcher = EmailFetcher(test_config)
    
    if not fetcher.authenticate():
        pytest.fail("Authentication failed despite token.json existing.")

    # 3. Fetch Real Data
    print("\n   📨 Fetching last 5 emails from Gmail...")
    # Fetch a small batch to keep test fast
    emails = fetcher.get_emails(max_results=5)
    
    assert isinstance(emails, list), "Fetcher should return a list"
    
    if not emails:
        print("   (Inbox is empty, skipping RAG check)")
        return

    # 4. Filter
    email_filter = EmailFilter()
    relevant_emails = email_filter.filter_relevant_emails(emails)
    print(f"   🔍 Found {len(relevant_emails)} relevant emails.")

    # 5. Index & Query (RAG)
    # We use the shared test configuration (which points to ./test_chroma_db)
    rag = EmailRAGSystem(test_config)
    rag.index_emails(relevant_emails)
    
    # Ask a question about the data we just fetched
    question = "Summarize the topics of these recent emails."
    answer = rag.answer_question(question)
    
    print(f"\n   Q: {question}")
    print(f"   A: {answer}")
    
    assert answer, "RAG should return an answer"
    assert "error" not in answer.lower(), "RAG should not error out"