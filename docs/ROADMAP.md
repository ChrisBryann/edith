# 🗺️ Edith Product Roadmap: Path to User Demo

## 🎯 Objective
Transition Edith from a developer prototype to a user-testable "Alpha" demo.

## Phase 1: The Foundation (React + Vite)
*Status: In Progress*

Users need a high-performance, responsive interface to interact with their data.
- [x] **Modern Web UI**: Replaced Streamlit with **React + Vite**.
    - **Architecture**: Single Page Application (SPA) talking to FastAPI backend.
    - **Chat Interface**: Persistent chat history with citation support.
    - **Sidebar HUD**: "Heads Up Display" showing "Today's Agenda" synced with Calendar.
- [x] **Visual Polish**:
    - Dark Mode premium aesthetic (`#212121` base).
    - **Flashcard UI**: Modeless, floating details for calendar events (no blocking overlays).
    - **Inline Expansion**: Quick-glance details in sidebar.

## Phase 2: Intelligence & Trust
*Priority: High*

The demo must feel "smart" and "safe".
- [x] **Mock Data Layer**: dedicated `edith/mocks/` architecture for robust demos.
- [x] **ML Filtering Integration**: TinyBERT model to separate Signal from Noise.
- [ ] **Contextual Awareness**:
    - Chat should understand *which* event you clicked on (e.g., "Summarize emails for *this* meeting").
    - **Citations**: Explicit links to source emails.

## Phase 3: Continuous Assistant Loop
*Priority: Medium*

Moving away from "Chatbots" to "Always-on Assistance".
- [x] **Remove "New Chat"**: Shift to a continuous timeline model.
- [ ] **Daily Briefing**: Auto-generated morning summary in the chat on load.
- [ ] **Async Syncing**: Background workers for email fetching to prevent UI freezes.

## Phase 4: Future Features
- [ ] **Voice Interaction**: Audio input/output.
- [ ] **Action Capabilities**: Draft replies, Accept/Decline invites directly from Flashcards.
- [ ] **Multi-Account View**: Unified Work + Personal dashboard.

## Phase 5: Expansions (Integrations)
Connecting Edith to the world.
- [ ] **MCP Server Support**:
    - Lib: `mcp` (Official Python SDK).
    - Goal: Connect to filesystem, database, or other local tools.
- [ ] **Outlook Integration**:
    - Lib: `msgraph-sdk` (Microsoft Graph).
    - Goal: Corporate email/calendar support.
- [ ] **Discord Integration**:
    - Lib: `discord.py`.
    - Goal: Summarize channel discussions, notify on mentions.
- [ ] **Notion Integration**:
    - Lib: `notion-client`.
    - Goal: Index knowledge base pages for RAG.