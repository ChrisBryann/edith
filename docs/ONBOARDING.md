# Developer Onboarding

Welcome to the Edith project! This guide will help you set up your development environment and understand how to work with the codebase.

## 🛠️ Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional, for containerized dev)
- A Google Cloud Project with Gmail & Calendar APIs enabled

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GMAIL_CREDENTIALS_PATH=credentials.json
CHROMA_DB_PATH=./chroma_db
GEMINI_MODEL=gemini-2.5-flash
EDITH_ENCRYPTION_KEY=  # Optional for dev (will auto-generate insecure key if missing)
EDITH_ENV=dev
```

### 3. Google API Setup

> **⚠️ Security Warning**
> **Never commit `credentials.json` or `token_*.json` files to a public repository.** These files should be listed in your `.gitignore`.

1. Go to Google Cloud Console.
2. Create a new project.
3. **Enable APIs**: Search for and enable "Gmail API" and "Google Calendar API".
4. **Configure OAuth Consent Screen**:
   - Select **External** user type.
   - Add your email address to **Test users**.
5. **Create Credentials**:
   - Go to **Credentials > Create Credentials > OAuth client ID**.
   - **Application type**: Desktop app.
   - Download the JSON file, rename it to `credentials.json`, and place it in the project root.

#### 👥 Collaborating with a Team

If a friend is developing with you, they do **not** need to create a new Google Cloud Project.

1. **Add them as a Test User**: Go to **OAuth consent screen** > **Test users** in your Google Cloud Console and add their email address.
2. **Share `credentials.json`**: Securely send them this file.
3. **Gemini API Key**: They can generate their own key or use yours.

### 4. Running the Application

#### CLI Mode (Interactive Chat)

This is the easiest way to test the RAG system with your real data.

```bash
python -m edith.main
```

#### API Mode (Backend Server)

Starts the FastAPI server for external integrations.

```bash
python -m edith.api
```

Access docs at: `http://localhost:8000/docs`

---

## 🐳 Docker Development

You can run Edith in a container to ensure a consistent environment.

**Note**: Authenticate locally first (`python -m edith.main`) to generate `token.json`. Docker will use this token to skip browser authentication.

### Run Interactive CLI

To chat with Edith inside Docker:

```bash
docker compose run --rm api python -m edith.main
```

### Run API Server

To start the backend service:

```bash
docker compose up
```

---

## 📡 API Reference

If running `api.py`, the following endpoints are available:

| Method   | Endpoint             | Description                                                          |
| -------- | -------------------- | -------------------------------------------------------------------- |
| `POST` | `/sync-emails`     | Triggers a background sync of recent emails.                         |
| `POST` | `/ask-question`    | Asks a question to the RAG system. JSON body:`{"question": "..."}` |
| `GET`  | `/email-summary`   | Returns a summary of emails from the last N days.                    |
| `GET`  | `/calendar-events` | Lists upcoming calendar events.                                      |
| `POST` | `/transcribe`      | Upload an audio file for transcription.                              |

---

## 🧪 Testing

We use `pytest` for automated backend testing. Currently, UI testing is performed manually.

### Backend Testing

Our backend tests cover unit logic (offline) and integration with Google APIs (online).

#### Datasets

Our test suite requires one or more datasets to be downloaded locally and placed in the `tests/datasets` folder.

Please download the following dataset and ensure it is named correctly:

1. **High Accuracy Email Classifier Dataset**
   Source: Hugging Face (jason23322)
   Link: [https://huggingface.co/datasets/jason23322/high-accuracy-email-classifier/resolve/main/full_dataset.csv](https://huggingface.co/datasets/jason23322/high-accuracy-email-classifier/resolve/main/full_dataset.csv)

   **After downloading, rename the file to `full_emails_dataset.csv`**

#### 1. Run Offline Tests (Fast)

These tests use mock data and do not require Google credentials. Run this frequently during development.

```bash
pytest -m offline
```

### Docker Testing

To run the test suite inside the Docker container:

```bash
docker compose run --rm api pytest
```

### Troubleshooting

If you see `404` errors regarding models, check your API key permissions or run `list_models.py` (if available) to see accessible Gemini models.
