# Edith: AI Personal Assistant

Edith is a strategic personal assistant designed to aggregate your digital life into a unified knowledge base. By connecting to your **Gmail** and **Google Calendar**, Edith allows you to ask natural language questions about your schedule, projects, and communications.

Instead of searching through dozens of threads, simply ask:
> *"What is the deadline for Project Phoenix?"*
> *"Summarize the emails from the marketing team this week."*
> *"Do I have any conflicts with the team meeting on Friday?"*

Edith uses **RAG (Retrieval Augmented Generation)** to securely index your data and **Google Gemini** to provide intelligent, context-aware answers.

## Features

- 📧 **Smart Email Search**: Ask questions across your inbox without keyword guessing.
- 📅 **Calendar Intelligence**: Understands your schedule in the context of your emails.
- 🛡️ **Privacy Focused**: Runs locally or in your own cloud; your data stays yours.
- 🧠 **Context Aware**: Filters out spam and focuses on relevant communications.

## 📚 Documentation

### For Developers
If you want to run Edith, contribute code, or understand how to set up the environment, please read the **Onboarding Guide**.

👉 **[Read ONBOARDING.md](ONBOARDING.md)**

### System Architecture
Interested in the technical design, data flows, and RAG implementation details?

👉 **Read assets/DESIGN.md**

## Development Roadmap

### Phase 1: MVP (Current)
- [x] Gmail integration
- [x] Basic email filtering
- [x] RAG system
- [x] Google Calendar integration
- [x] REST API

### Phase 2: Voice & Audio Intelligence
- [ ] **Voice Interface**: Speech-to-Text (STT) and Text-to-Speech (TTS) for hands-free interaction
- [ ] **Audio Ingestion**: Pipeline for recorded calls and meetings
- [ ] **Transcription**: Auto-transcribe audio content for RAG indexing

### Phase 3: Knowledge Base Expansion
- [ ] **Notion Integration**: Index workspaces and pages
- [ ] **Document Support**: PDF, Docx, and Obsidian/Markdown notes
- [ ] **Unified Search**: Query across emails, calendar, and notes simultaneously

## License

MIT License - see LICENSE file for details
