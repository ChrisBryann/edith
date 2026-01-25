import os
from dotenv import load_dotenv

# Import our modular services
from config import EmailAssistantConfig
from gmail_service import GmailService
from calendar_service import CalendarService
from email_rag import EmailRAGSystem
from email_filter import EmailFilter

def main():
    # 1. Load Environment
    load_dotenv()
    print("🤖 Initializing Edith (CLI Mode)...")

    config = EmailAssistantConfig()
    
    # Check for API Key
    if not config.gemini_api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables.")
        return

    # 2. Initialize Services
    gmail_service = GmailService(config)
    calendar_service = CalendarService(config)
    email_filter = EmailFilter()
    rag_system = EmailRAGSystem(config)

    # 3. Authenticate
    print("\n🔐 Authenticating with Google...")
    if gmail_service.authenticate():
        print("   ✅ Gmail Authenticated")
        # Share credentials with Calendar
        if gmail_service.creds:
            calendar_service.authenticate(gmail_service.creds)
            print("   ✅ Calendar Authenticated")
    else:
        print("   ❌ Authentication failed.")
        return

    # 4. Sync Data (Optional for CLI demo)
    print("\n📨 Fetching recent emails...")
    emails = gmail_service.get_emails(max_results=20)
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