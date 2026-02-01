import streamlit as st
import requests
import os
import time
from datetime import datetime

# Configuration
# When running in Docker, this should point to the container name (http://api:8000)
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Edith AI",
    page_icon="🤖",
    layout="wide"
)

st.title("Edith")

# --- Onboarding & Status Logic ---

def get_system_status():
    try:
        return requests.get(f"{API_URL}/system-status", timeout=2).json()
    except:
        return None

status = get_system_status()

if not status:
    st.error("🔴 Cannot connect to Edith API. Is it running?")
    st.stop()

# 1. Authentication Check
if not status.get("is_authenticated"):
    st.warning("🔐 Edith is not authenticated with Gmail.")
    st.info("Please check the server console/logs to complete the authentication flow, or ensure 'token.json' is present.")
    if st.button("Check Again"):
        st.rerun()
    st.stop()

# 2. Sync Status Check
sync_state = status.get("sync_state")
is_ready = status.get("is_ready")

if sync_state == "idle" and not is_ready:
    st.info("👋 Welcome! Let's load your recent emails to get started.")
    st.markdown("""
    Edith needs to build a knowledge base from your emails.
    - We will fetch emails from the last **1 month** (capped at 500 for speed).
    - You can start asking questions once we've processed the last **7 days**.
    """)
    
    if st.button("🚀 Start Initial Sync"):
        try:
            requests.post(f"{API_URL}/sync-emails")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to start sync: {e}")
    st.stop()

elif sync_state == "syncing":
    st.subheader("🔄 Syncing your digital life...")
    
    # Progress Bar
    progress_container = st.empty()
    status_text = st.empty()
    
    # Poll for updates
    count = status.get("sync_progress", 0)
    msg = status.get("sync_message", "")
    
    st.progress(min(count % 100, 100)) # Indeterminate visual
    st.write(f"**Status:** {msg}")
    
    if is_ready:
        st.success("✅ Enough data loaded! You can start using Edith while we finish up.")
    else:
        st.info("Please wait, Edith is learning...")
        time.sleep(2)
        st.rerun()

elif sync_state == "error":
    st.error("❌ An error occurred during sync.")
    st.write(status.get("sync_message"))
    if st.button("Retry"):
        requests.post(f"{API_URL}/sync-emails")
        st.rerun()

# If we are here, we are either ready or syncing-but-ready

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Context & Briefing ---
with st.sidebar:
    st.header("📅 Daily Briefing")
    
    # 1. Calendar Events
    st.subheader("Upcoming Events")
    try:
        # Fetch events for the next 3 days
        response = requests.get(f"{API_URL}/calendar-events", params={"days_ahead": 3}, timeout=5)
        if response.status_code == 200:
            events = response.json()
            if events:
                for event in events:
                    # Parse ISO format (handling Z for UTC)
                    start_dt = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                    time_str = start_dt.strftime("%I:%M %p")
                    date_str = start_dt.strftime("%b %d")
                    
                    st.markdown(f"**{event['title']}**")
                    st.caption(f"🗓️ {date_str} at {time_str}")
                    st.divider()
            else:
                st.info("No upcoming events found.")
        else:
            st.warning("Could not fetch calendar.")
    except Exception as e:
        st.error(f"API Connection Error: {e}")

    # 2. Email Summary
    st.subheader("Inbox Summary")
    if st.button("Generate Weekly Summary"):
        with st.spinner("Analyzing emails..."):
            try:
                response = requests.get(f"{API_URL}/email-summary", params={"days": 7}, timeout=30)
                if response.status_code == 200:
                    summary = response.json().get("summary", "No summary available.")
                    st.success("Updated!")
                    st.markdown(summary)
                else:
                    st.error("Failed to generate summary.")
            except Exception:
                st.error("API unreachable.")

# --- Main Chat Interface ---

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask about your emails, schedule, or projects..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            response = requests.post(
                f"{API_URL}/ask-question", 
                json={"question": prompt},
                timeout=60 # RAG can be slow
            )
            
            if response.status_code == 200:
                answer = response.json().get("answer", "I couldn't get an answer.")
                message_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                error_msg = "Sorry, I encountered an error processing your request."
                message_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
        except Exception as e:
            error_msg = f"Error connecting to Edith API: {e}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})