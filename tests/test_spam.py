import pytest

pytestmark = pytest.mark.offline

def test_spam_detection(spam_llm_service, dummy_emails):
    """Tests Spam Detection LLM service if it can detect spam emails correctly"""
    
    # preprocess emails
    emails = dummy_emails
    inputs = []
    for email in emails:
        inputs.append(f"Subject: {email.subject}\n\b{email.body}")
        
    preds = spam_llm_service.detect_spam(inputs)
    
    print(preds)
        