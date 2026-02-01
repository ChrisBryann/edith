# Edith: AI Personal Assistant

Edith is a strategic personal assistant designed to aggregate your digital life into a unified knowledge base. By connecting to your **Gmail** and **Google Calendar**, Edith allows you to ask natural language questions about your schedule, projects, and communications.

Instead of searching through dozens of threads, simply ask:
> *"What is the deadline for Project Phoenix?"*
>
> *"Summarize the emails from the marketing team this week."*
>
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

👉 **[Read docs/ONBOARDING.md](docs/ONBOARDING.md)**

### System Architecture
Interested in the technical design, data flows, and RAG implementation details?

👉 **[Read docs/DESIGN.md](docs/DESIGN.md)**

## Development Roadmap

We are currently transitioning from **MVP** to **Alpha Demo**.

👉 **[View the Detailed Roadmap](docs/ROADMAP.md)**

### Upcoming Milestones
- **Frontend UI**: A Streamlit-based web interface.
- **ML Filtering**: Advanced noise reduction using TinyBERT.
- **Demo Mode**: One-click setup with dummy data for user testing.

### Phase 3: Knowledge Base Expansion
- [ ] **Notion Integration**: Index workspaces and pages
- [ ] **Document Support**: PDF, Docx, and Obsidian/Markdown notes
- [ ] **Unified Search**: Query across emails, calendar, and notes simultaneously

## License

MIT License - see LICENSE file for details
