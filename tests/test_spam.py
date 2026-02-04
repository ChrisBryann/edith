import pytest
from tests.decorators.spam_metrics import spam_metrics
pytestmark = pytest.mark.offline

def test_get_true_metrics(dummy_live_emails):
    true_pos = true_neg = 0
    for email in dummy_live_emails:
        if email.is_relevant:
            true_pos += 1
        else:
            true_neg += 1
    
    print(f'{test_get_true_metrics.__name__} - Got {len(dummy_live_emails)} live email dummy data.\nTP (True Positives): {true_pos}\nTN (True Negatives): {true_neg}')

def test_single_spam_ml_detection(email_filter, dummy_single_email):
    """Tests Spam Detection ML LLM service from Email Filter service if it can identify spam/no spam on single email"""
    
    print(email_filter._is_spam_ml(dummy_single_email))

@spam_metrics
def test_spam_ml_detection(email_filter, dummy_live_emails):
    """Tests Spam Detection ML LLM service from Email Filter service if it can detect spam emails correctly"""
    for email in dummy_live_emails:
        is_spam = email_filter._is_spam_ml(email)
        test_spam_ml_detection._record(
            expected_is_spam=is_spam,
            predicted_is_spam=not email.is_relevant,
        )

@spam_metrics
def test_spam_heuristics_detection(email_filter, dummy_live_emails):
    """Tests heuristic classification of email to detect spam or not"""
    

    for email in dummy_live_emails:
        is_relevant = email_filter._is_relevant(email)
        test_spam_heuristics_detection._record(
            expected_is_spam=is_relevant,
            predicted_is_spam=email.is_relevant,
        )
@spam_metrics
def test_spam_ml_heuristics_detection(email_filter, dummy_live_emails):
    """Tests ML LLM detection first and pass the rest of the relevant ones through heuristics filtering for spam emails or not"""

    relevant_emails = []
    
    for i, email in enumerate(dummy_live_emails):
        is_spam = email_filter._is_spam_ml(email)
        if not is_spam:
            relevant_emails.append(i)
        else:
            test_spam_ml_heuristics_detection._record(
                expected_is_spam=not is_spam,
                predicted_is_spam=email.is_relevant,
            )   
        
    
    # after getting the emails that are not spam from ML filtering,
    # filter using heuristic scoring
    
    for i in relevant_emails:
        email = dummy_live_emails[i]
        is_relevant = email_filter._is_relevant(email)
        test_spam_ml_heuristics_detection._record(
            expected_is_spam=is_relevant,
            predicted_is_spam=email.is_relevant,
        )
        
        
@spam_metrics
def test_spam_heuristics_ml_detection(email_filter, dummy_live_emails):
    """Tests heuristics filtering first and pass the rest of the relevant ones through ML LLM detection for spam emails or not"""

    relevant_emails = []
    
    for i, email in enumerate(dummy_live_emails):
        is_relevant = email_filter._is_relevant(email)
        if is_relevant:
            relevant_emails.append(i)
        else:
            test_spam_heuristics_ml_detection._record(
                expected_is_spam=is_relevant,
                predicted_is_spam=email.is_relevant,
            )
    
    # after getting the emails that are not spam from heuristics filtering,
    # filter using ML detection
    
    for i in relevant_emails:
        email = dummy_live_emails[i]
        is_spam = email_filter._is_spam_ml(email)
        test_spam_heuristics_ml_detection._record(
            expected_is_spam=not is_spam,
            predicted_is_spam=email.is_relevant,
        )
        
@spam_metrics
def test_spam_heuristics_ml_combined_detection(email_filter, dummy_live_emails):
    """Tests heuristics filtering first and ML LLM detection TOGETHER for spam emails or not"""
    
    for email in dummy_live_emails:
        is_relevant = not email_filter._is_spam_ml(email) or email_filter._is_relevant(email)
        test_spam_heuristics_ml_combined_detection._record(
            expected_is_spam=is_relevant,
            predicted_is_spam=email.is_relevant,
        )