import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import transcribe

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env.local")
print(f"DEBUG: Loading .env from: {env_path}")
print(f"DEBUG: .env file exists: {os.path.exists(env_path)}")
load_dotenv(env_path)

app = FastAPI(title="Meeting Transcription API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcribe.router, prefix="/api/v1", tags=["transcription"])

@app.get("/")
def read_root():
    return {"message": "Meeting Transcription API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
