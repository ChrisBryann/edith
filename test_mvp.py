#!/usr/bin/env python3

import sys
import os
import shutil
import time
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import EmailAssistantConfig
from models import EmailMessage
from services.email.rag import EmailRAGSystem

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

def run_rag_test():
    print("🧪 Starting RAG System Test Suite")
    print("=" * 60)

    # 0. Load Environment Variables
    load_dotenv()
    os.environ["EDITH_ENV"] = "test"

    # 1. Configuration
    config = EmailAssistantConfig()
    
    # Cleanup previous test runs
    if os.path.exists(config.chroma_db_path):
        shutil.rmtree(config.chroma_db_path)

    try:
        # 2. Initialize System
        print("1. Initializing RAG System...")
        if not config.gemini_api_key:
            print("   ❌ GEMINI_API_KEY not found. Please set it in .env")
            return

        rag = EmailRAGSystem(config)
        print(f"   🤖 Using Gemini Model: {config.gemini_model}")
        print("   ✅ System initialized")

        # 3. Ingest Data
        print("\n2. Ingesting Dummy Data...")
        emails = get_dummy_data()
        rag.index_emails(emails)
        print(f"   ✅ Indexed {len([e for e in emails if e.is_relevant])} relevant emails")

        # 4. Test Cases
        test_cases = [
            {
                "scenario": "Work Deadline",
                "question": "When is the deadline for Project Phoenix?",
                "expected": ["November 15", "Friday"]
            },
            {
                "scenario": "Technical Details",
                "question": "What port is the staging environment using?",
                "expected": ["8080"]
            },
            {
                "scenario": "Personal Event Location",
                "question": "Where is Mom's birthday party?",
                "expected": ["Italian Place", "Main St"]
            },
            {
                "scenario": "Travel Details",
                "question": "What is my seat number for the Tokyo flight?",
                "expected": ["14A"]
            },
            {
                "scenario": "Negative Test (Missing Info)",
                "question": "What is the budget for Project Phoenix?",
                "expected": ["not found", "no information", "don't know", "cannot answer"]
            }
        ]

        print("\n3. Running Query Tests...")
        passed_count = 0
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n   Test Case {i}: {case['scenario']}")
            print(f"   Q: {case['question']}")
            
            # Measure latency
            start_time = time.time()
            answer = rag.answer_question(case['question'])
            duration = time.time() - start_time
            
            print(f"   A: {answer}")
            print(f"   ⏱️  {duration:.2f}s")
            
            # Verification
            is_passed = False
            if case['scenario'].startswith("Negative"):
                # For negative tests, check for common refusal phrases
                negative_phrases = ["not mention", "no information", "couldn't find", "don't have", "sorry"]
                if any(phrase in answer.lower() for phrase in negative_phrases):
                    is_passed = True
            else:
                # Check for expected keywords
                if any(exp.lower() in answer.lower() for exp in case['expected']):
                    is_passed = True
            
            if is_passed:
                print("   ✅ PASS")
                passed_count += 1
            else:
                print(f"   ⚠️  CHECK MANUALLY (Expected: {case['expected']})")

        # Test Case 6: Audio Transcription (Mock)
        print(f"\n   Test Case 6: Audio Transcription (Connectivity Check)")
        try:
            # Create dummy mp3 header bytes
            dummy_audio = b'\xFF\xF3\x44\xC4' + b'\x00' * 100
            transcript = rag.transcribe_audio(dummy_audio)
            print(f"   A: [Transcript Length: {len(transcript)}] {transcript[:50]}...")
            # We expect Gemini to either try to transcribe or complain about the file format, 
            # but NOT throw a connection error.
            print("   ✅ PASS (API Connected)")
            passed_count += 1
        except Exception as e:
            print(f"   ❌ FAIL: {e}")

        print("\n" + "=" * 60)
        print(f"Test Summary: {passed_count}/{len(test_cases) + 1} tests passed automated checks.")
        
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(config.chroma_db_path):
            shutil.rmtree(config.chroma_db_path)
            print("\n🧹 Cleaned up test database.")

if __name__ == "__main__":
    run_rag_test()