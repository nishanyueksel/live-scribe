from pydantic import BaseModel
from typing import List

class TranscriptResponse(BaseModel):
    transcript: str
    summary: str
    action_items: List[str]