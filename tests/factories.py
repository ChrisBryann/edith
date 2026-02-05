from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd

from edith.lib.shared.models.email import EmailMessage

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
            account_type="work",
            cc_emails=[],
            is_unread=False,
            to_emails=[],
            thread_id=None
        ),
        # Scenario 2: Technical Details
        EmailMessage(
            id="work_2",
            subject="Phoenix API Specs",
            sender="lead@techcorp.com",
            body="For the Phoenix API, we are using port 8080 for the staging environment and port 3000 for dev. The API key for staging is STAGING_KEY_99.",
            date=base_date - timedelta(days=1),
            is_relevant=True,
            account_type="work",
            cc_emails=[],
            headers=[],
            is_unread=False,
            to_emails=[],
            thread_id=None
        ),
        # Scenario 3: Personal Event
        EmailMessage(
            id="personal_1",
            subject="Mom's Surprise Party",
            sender="sister@family.com",
            body="We are hosting Mom's 60th birthday at The Italian Place on Main St. It's this Saturday at 7 PM. Don't forget to bring the photo album!",
            date=base_date - timedelta(days=3),
            is_relevant=True,
            account_type="personal",
            cc_emails=[],
            headers=[],
            is_unread=True,
            to_emails=[],
            thread_id=None
        ),
        # Scenario 4: Travel
        EmailMessage(
            id="travel_1",
            subject="Flight Confirmation: NYC to Tokyo",
            sender="bookings@airline.com",
            body="Your flight JL005 departs from JFK Terminal 1 on Dec 20th at 12:30 PM. Seat 14A confirmed.",
            date=base_date - timedelta(days=5),
            is_relevant=True,
            account_type="personal",
            cc_emails=[],
            headers=[],
            is_unread=False,
            to_emails=[],
            thread_id=None
        ),
        # Scenario 5: Irrelevant Email (Should be skipped by RAG if is_relevant=False)
        EmailMessage(
            id="spam_1",
            subject="IMPORTANT! Win a free iPhone! Claim it now!",
            sender="promo@spam.com",
            body="Click here to claim your prize now!",
            date=base_date,
            is_relevant=False,
            account_type="personal",
            cc_emails=[],
            headers=[],
            is_unread=True,
            to_emails=[],
            thread_id=None
        )
    ]
    
def get_dummy_live_data(limit : Optional[int] = None) -> List[EmailMessage]:
    """Gets dummy live data from Huggingface dataset"""
    
    emails_df = pd.read_csv('tests/datasets/full_emails_dataset.csv')
    live_emails = []
    base_date = datetime.now()
    
    iterrows = list(emails_df.iterrows())
    limit = limit if limit is not None else len(iterrows)
    
    for i in range(limit):
        _, row = iterrows[i]
        is_relevant = False if 1 <= row['category_id'] <= 3 else True # False if category is Promotions, Social Media, or Spam
        live_emails.append(EmailMessage(
            id=row['id'],
            subject=row['subject'],
            sender="test@live_emails.com",
            body=row['body'],
            date=base_date,
            is_relevant=is_relevant,
            account_type="personal",
            cc_emails=[],
            headers=[],
            is_unread=True,
            to_emails=[],
            thread_id=None
        ))
    
    return live_emails
