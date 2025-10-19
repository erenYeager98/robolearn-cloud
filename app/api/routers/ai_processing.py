# app/api/routers/ai_processing.py

from fastapi import APIRouter, HTTPException
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
            emotion=query.emotion,
            level=query.level
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
@router.post("/analyze-image")
async def analyze_image_endpoint(payload: ImagePayload):
    try:
        # A data URL looks like "data:image/png;base64,iVBORw0KGgo..."
        # We need to extract the mime type and the actual base64 data
        header, encoded_data = payload.image_data.split(',', 1)
        
        # Extract mime type (e.g., 'image/png')
        match = re.search(r'data:(?P<mime_type>[\w/]+);base64', header)
        if not match:
            raise HTTPException(status_code=400, detail="Invalid Base64 data URL format")
        mime_type = match.group('mime_type')

        # Decode the Base64 string into bytes
        image_bytes = base64.b64decode(encoded_data)
        
        # Call the service function with the decoded bytes and mime type
        model_output = await ai_service.analyze_image_with_gemini(
            image_bytes=image_bytes, 
            mime_type=mime_type
        )
        
        return {"filename": "image.png", "response": model_output} # Filename is now generic
    except (base64.binascii.Error, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid Base64 data: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/gen_keywords")
async def generate_images_endpoint(query: ResearchQuery):
    """
    This endpoint takes a question and an emotion, generates relevant keywords,
    and returns a list of image URLs from the Serper API.
    """
    try:
        image_urls = await ai_service.generate_image_urls(
            question=query.question,
            emotion=query.emotion
        )
        if not image_urls:
            # This could happen if the API returns no results or an error occurred
            # in the service layer that was handled gracefully.
            return {"image_urls": []}
            
        return {"image_urls": image_urls}
    except Exception as e:
        # This catches unexpected errors during the process.
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")