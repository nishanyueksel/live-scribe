import whisper
import torch
import os
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment


def chunk_audio(audio_file_path, chunk_length_ms=30000):
    audio = AudioSegment.from_file(audio_file_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i+chunk_length_ms]
        chunk_path = f"{audio_file_path}_chunk_{i//chunk_length_ms}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks
class WhisperService:
    async def transcribe_stream(self, audio_file_path: str):
        import asyncio
        chunk_paths = []
        try:
            # Use the fixed chunk_audio function
            chunk_paths = chunk_audio(audio_file_path, chunk_length_ms=30000)
            print(f"Created {len(chunk_paths)} chunks for processing")

            for i, chunk_path in enumerate(chunk_paths):
                try:
                    print(f"Processing chunk {i+1}/{len(chunk_paths)}: {chunk_path}")

                    # Run the synchronous transcribe in a thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, self.model.transcribe, chunk_path)

                    text = result["text"].strip()
                    print(f"Chunk {i+1} transcribed: '{text[:50]}...'")

                    if text:  # Only yield non-empty text
                        yield text
                    else:
                        print(f"Chunk {i+1} produced empty text, skipping")

                except Exception as e:
                    print(f"Error transcribing chunk {chunk_path}: {str(e)}")
                    # Continue with next chunk instead of failing completely
                    yield f"[Error processing audio segment {i+1}]"
                finally:
                    # Clean up this chunk file
                    if os.path.exists(chunk_path):
                        os.remove(chunk_path)
                        print(f"Cleaned up chunk file: {chunk_path}")

            print("All chunks processed successfully")
        except Exception as e:
            print(f"Error in transcribe_stream: {str(e)}")
            raise
        finally:
            # Clean up any remaining chunk files
            for chunk_path in chunk_paths:
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
                    print(f"Final cleanup: {chunk_path}")
    def __init__(self, model_name="base", openai_api_key=None):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_name, device=device)

        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        print(f"DEBUG: API key found: {bool(api_key)}")
        print(f"DEBUG: API key length: {len(api_key) if api_key else 0}")
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None
    async def transcribe(self, audio_file_path: str) -> str:
        chunks = chunk_audio(audio_file_path, chunk_length_ms=30000)
        transcript_parts = []
    
        for chunk in chunks:
            result = self.model.transcribe(chunk)
            transcript_parts.append(result["text"])
    
        return " ".join(transcript_parts)
    
    async def summarize_and_extract(self, transcript: str) -> dict:
        """
        Use OpenAI API to generate both a concise summary and structured action items.
        Returns a dict with keys: 'summary' and 'action_items'.
        """
        prompt = f"""
You are an AI executive assistant specializing in comprehensive meeting analysis.
Your task is to process the provided meeting transcript and return a detailed structured JSON object.

The meeting transcript is provided below, enclosed in triple quotes:
\"\"\"
{transcript}
\"\"\"

Based on the transcript, generate a single JSON object with the following exact structure:

1. "summary": A comprehensive but focused summary (6 to 12 sentences) covering:
   - Main discussion topics and key decisions
   - Important outcomes and next steps
   - Notable concerns or challenges mentioned

2. "action_items": An array of objects representing the most important actionable items (aim for 3-8 items). Each object must have:
   - "task": Detailed description of the specific task or responsibility
   - "deadline": Due date or timeframe; if not specified, use "Not Specified"

   Include items like:
   - Follow-up tasks
   - Research assignments
   - Preparation for future meetings
   - Documents to be created or reviewed
   - People to contact or coordinate with
   - Decisions to be communicated
   - Process improvements or changes to implement

Focus on quality over quantity. Extract the most important and actionable items rather than everything mentioned. Prioritize clarity and usefulness.

Output must be valid JSON only, no extra text or commentary.
"""

        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Please provide an API key.")

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content
        
        # Convert the JSON string returned by OpenAI to a Python dict
        import json
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback if the model adds stray characters
            # Extract the first JSON object in the string
            import re
            match = re.search(r"{.*}", content, flags=re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError("OpenAI returned invalid JSON")
