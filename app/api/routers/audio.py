# app/api/routers/audio.py

from fastapi import APIRouter, File, UploadFile, HTTPException, Response
from fastapi.responses import JSONResponse
from app.models.schemas import TTSRequest
from app.services import audio_service

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    # GCP Speech-to-Text supports webm directly
    if not file.content_type.startswith("audio/"):
         raise HTTPException(status_code=400, detail="Invalid file type, must be audio.")
    try:
        audio_content = await file.read()
        transcription = await audio_service.transcribe_audio_gcp(audio_content)
        return JSONResponse(content={"prompt": "Say something about your favorite technology.", "transcription": transcription})
    except Exception as e:
        print(e);
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-speech")
async def text_to_speech_endpoint(request: TTSRequest):
    try:
        audio_data = await audio_service.generate_tts_audio_gcp(request.text)
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as e:
        print(f"ERROR in /text-to-speech: {e}") # Also print to server logs
        raise HTTPException(status_code=500, detail=str(e))