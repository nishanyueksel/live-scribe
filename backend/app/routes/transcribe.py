import os
import tempfile
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from app.models.transcript import TranscriptResponse
from app.services.whisper_service import WhisperService
from app.services.pdf_service import PDFService

router = APIRouter()
pdf_service = PDFService()

# Store uploaded files temporarily with job IDs
uploaded_files = {}

class PDFExportRequest(BaseModel):
    transcript: str
    summary: str
    action_items: list[str]

class UploadResponse(BaseModel):
    job_id: str
    filename: str
    message: str

def get_whisper_service():
    return WhisperService(openai_api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/upload", response_model=UploadResponse)
async def upload_audio(file: UploadFile = File(...)):
    """Upload audio file and return a job ID for streaming transcription"""
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")

    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())

        # Save to temp file
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Store file path with job ID
        uploaded_files[job_id] = {
            "file_path": tmp_path,
            "filename": file.filename,
            "created_at": os.path.getmtime(tmp_path)
        }

        return UploadResponse(
            job_id=job_id,
            filename=file.filename,
            message="File uploaded successfully. Use job_id to start transcription."
        )

    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transcribe/{job_id}")
async def transcribe_stream(job_id: str, whisper_service: WhisperService = Depends(get_whisper_service)):
    """Stream transcription results for uploaded file using job ID"""
    if job_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="Job ID not found")

    file_info = uploaded_files[job_id]
    tmp_path = file_info["file_path"]

    if not os.path.exists(tmp_path):
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    async def event_stream():
        try:
            print(f"Starting transcription stream for job {job_id}")
            chunk_count = 0
            async for chunk_text in whisper_service.transcribe_stream(tmp_path):
                chunk_count += 1
                print(f"Streaming chunk {chunk_count}: '{chunk_text[:50]}...'")
                # SSE requires "data:" prefix and double linebreak
                yield f"data: {chunk_text}\n\n"

            # Send completion signal
            print(f"Transcription complete for job {job_id}, sent {chunk_count} chunks")
            yield "data: [TRANSCRIPTION_COMPLETE]\n\n"

        except Exception as e:
            print(f"Error during streaming transcription: {str(e)}")
            import traceback
            traceback.print_exc()
            yield f"data: [ERROR: {str(e)}]\n\n"
        finally:
            # Clean up temp file and job entry after streaming is complete
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                print(f"Cleaned up temp file: {tmp_path}")
            if job_id in uploaded_files:
                del uploaded_files[job_id]
                print(f"Removed job {job_id} from memory")

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.post("/transcribe", response_model=TranscriptResponse)
async def transcribe_audio(file: UploadFile = File(...), whisper_service: WhisperService = Depends(get_whisper_service)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")

    try:
        # Save to temp filel
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        async def event_stream():
            try:
                async for chunk_text in whisper_service.transcribe_stream(tmp_path):
                    # SSE requires "data:" prefix and double linebreak
                    yield f"data: {chunk_text}\n\n"
            finally:
                # Clean up temp file after streaming is complete
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        return StreamingResponse(event_stream(), media_type="text/event-stream")
        # # Run whisper
        # transcript_text = await whisper_service.transcribe(tmp_path)

        # # Clean up temp file
        # os.remove(tmp_path)

        # # Get summary and action items using OpenAI
        # result = await whisper_service.summarize_and_extract(transcript_text)

        # # Convert action item objects to strings
        # formatted_action_items = []
        # for item in result["action_items"]:
        #     if item["deadline"] == "Not Specified":
        #         formatted_action_items.append(item["task"])
        #     else:
        #         formatted_action_items.append(f"{item['task']} (Due: {item['deadline']})")

        # return TranscriptResponse(
        #     transcript=transcript_text,
        #     summary=result["summary"],
        #     action_items=formatted_action_items,
        # )

    except Exception as e:
        import traceback
        print(f"Error during transcription: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        # Clean up temp file if error occurs before streaming starts
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export-pdf")
async def export_pdf(request: PDFExportRequest):
    """Export transcript, summary, and action items to PDF"""
    try:
        pdf_bytes = pdf_service.generate_transcript_pdf(
            transcript=request.transcript,
            summary=request.summary,
            action_items=request.action_items
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=meeting_transcript.pdf"
            }
        )
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
