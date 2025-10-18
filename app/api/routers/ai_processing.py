# app/api/routers/ai_processing.py

from fastapi import APIRouter, HTTPException, UploadFile
# Note: We no longer need UploadFile or File from fastapi here
from app.models.schemas import ResearchQuery, SummarizeRequest, ImagePayload # <-- Import ImagePayload
from app.services import ai_service
import base64
import re

router = APIRouter()

# --- research_endpoint and summarize_endpoint remain the same ---

@router.post("/research")
async def research_endpoint(query: ResearchQuery):
    try:
        answer = await ai_service.generate_research_response_with_gemini(
            question=query.question,
            emotion=query.emotion
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def summarize_endpoint(request: SummarizeRequest):
    try:
        summary = await ai_service.generate_summary_with_gemini(request.content)
        return {"answer": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- THIS IS THE CORRECTED ENDPOINT ---
@router.post("/upload-image") # Matches the URL in your JS
async def handle_image_upload(file: UploadFile = File(...)):
    # Check if the uploaded file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    try:
        # Read the raw bytes from the uploaded file
        image_bytes = await file.read()
        
        # Call your Gemini service function with the bytes
        analysis_result = await ai_service.analyze_image_with_gemini(
            image_bytes=image_bytes,
            mime_type=file.content_type
        )
        
        # Return the result
        return {"filename": file.filename, "response": analysis_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))