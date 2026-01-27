import os
import shutil
from dotenv import load_dotenv

# Import our modular services
from config import EmailAssistantConfig, Environment
from gmail_service import GmailService
from calendar_service import CalendarService
from email_rag import EmailRAGSystem
from email_filter import EmailFilter

def main():
    # 1. Load Environment
    load_dotenv()
    print("🤖 Initializing Edith (CLI Mode)...")

    config = EmailAssistantConfig()
    print(f"   🌍 Environment: {config.env.value}")
    print(f"   🎭 Mock Data: {config.use_mock_data}")
    
    # Check for API Key
    if not config.gemini_api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables.")
        return

    # Clear DB for fresh start in CLI mode (only in DEV)
    if config.env == Environment.DEV and os.path.exists(config.chroma_db_path):
        print(f"🧹 Clearing existing database at {config.chroma_db_path}...")
        shutil.rmtree(config.chroma_db_path)

    # 2. Initialize Services
    gmail_service = GmailService(config)
    calendar_service = CalendarService(config)
    email_filter = EmailFilter()
    rag_system = EmailRAGSystem(config)

    # 3. Authenticate
    print("\n🔐 Authenticating with Google...")
    if gmail_service.authenticate():
        print("   ✅ Gmail Authenticated")
        
        # Fetch and configure email account (Critical for CalendarService)
        user_email = gmail_service.get_profile_email()
        config.add_email_account(user_email, is_primary=True)
        print(f"   📧 Logged in as: {user_email}")

        # Share credentials with Calendar
        if gmail_service.creds:
            calendar_service.authenticate(gmail_service.creds)
            print("   ✅ Calendar Authenticated")
    else:
        print("   ❌ Authentication failed.")
        return

    # 4. Sync Data (Optional for CLI demo)
    print("\n📨 Fetching recent emails...")
    # Fetching 100 emails from the last 30 days (filtering at API level for efficiency)
    emails = gmail_service.get_emails(max_results=100, query="newer_than:30d")
    relevant_emails = email_filter.filter_relevant_emails(emails)
    print(f"   Found {len(emails)} emails, {len(relevant_emails)} deemed relevant.")
    
    if relevant_emails:
        print("   🧠 Indexing emails into RAG system...")
        rag_system.index_emails(relevant_emails)

    # 5. Interactive Loop
    print("\n✨ Edith is ready! (Type 'exit' to quit)")
    print("-" * 50)
    
    while True:
        query = input("\nYou: ")
        if query.lower() in ['exit', 'quit']:
            break
        
        # Fetch fresh calendar context for every question
        events = calendar_service.get_events(days_ahead=7)
        calendar_context = "\n".join([f"- {e.title} at {e.start_time}" for e in events])
        
        response = rag_system.answer_question(query, additional_context=calendar_context)
        print(f"Edith: {response}")

if __name__ == "__main__":
    main()