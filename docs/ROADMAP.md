# 🗺️ Edith Product Roadmap: Path to User Demo

## 🎯 Objective
Transition Edith from a developer prototype to a user-testable "Alpha" demo.

## Phase 1: The User Experience (Frontend)
*Priority: Critical | Timeline: 1 Week*

Users need a visual interface to interact with their data.
- [ ] **Web UI (Streamlit)**: Build a lightweight frontend using Streamlit.
    - **Architecture**: Connects to the `api` service via HTTP (Client-Server model).
    - **Chat Interface**: A familiar chat bubble UI for Q&A.
    - **Sidebar Dashboard**: Display "Today's Summary" and "Upcoming Events" persistently.
    - **Debug Panel**: Toggle to show retrieved emails (transparency builds trust).
- [ ] **Visual Feedback**: Loading states (spinners) while RAG is processing.

## Phase 2: Intelligence & Trust
*Priority: High | Timeline: 1-2 Weeks*

The demo must feel "smart" and "safe".
- [ ] **ML Filtering Integration**: Replace current heuristics with the TinyBERT model to ensure spam doesn't pollute the demo.
- [ ] **Citations**: When Edith answers, it must list the specific emails used as sources (e.g., *"Source: Email from John, Oct 12"*).
- [ ] **"Demo Mode"**: A launch option that loads the `test_mvp.py` dummy data. This allows you to demo the UI to users without needing their real Google credentials immediately.

## Phase 3: Performance & Polish
*Priority: Medium | Timeline: 1 Week*

- [ ] **Async Syncing**: Ensure the UI doesn't freeze while fetching new emails (move `sync_emails` to a true background worker).
- [ ] **Error Handling**: Graceful messages when the Gmail API quota is hit or auth fails.
- [ ] **Deployment**: A `docker-compose.yml` setup that spins up both the API and the Streamlit UI with one command.

## Phase 4: Future Features (Post-Demo)
- [ ] **Voice Interaction**: Audio input for queries.
- [ ] **Write Capabilities**: Draft email replies (currently read-only).
- [ ] **Multi-Account Support**: Unified view for Work + Personal emails.