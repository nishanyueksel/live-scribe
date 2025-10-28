# Meeting Transcription Backend

FastAPI backend for transcribing audio files and generating summaries with action items.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/v1/transcribe` - Upload audio file for transcription

## Project Structure

```
backend/
├── app/
│   ├── main.py            # FastAPI entrypoint
│   ├── routes/            # API route definitions
│   │   └── transcribe.py  # Transcription endpoints
│   ├── services/          # Business logic
│   │   └── whisper_service.py
│   └── models/            # Pydantic models
│       └── transcript.py
├── requirements.txt
└── .gitignore
```