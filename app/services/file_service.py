# app/services/file_service.py

import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from google.cloud import storage
from app.core.config import settings

def upload_file_to_gcs(file: UploadFile, file_bytes: bytes) -> str:
    """Uploads a file to GCS and returns its public URL."""
    if not settings.GCS_BUCKET_NAME:
        raise ValueError("GCS_BUCKET_NAME is not set in the configuration.")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")

    client = storage.Client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    
    suffix = Path(file.filename).suffix or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    
    blob = bucket.blob(unique_name)
    
    # Upload the file bytes
    blob.upload_from_string(
        data=file_bytes,
        content_type=file.content_type
    )
    
    # Make the blob publicly viewable
    blob.make_public()
    
    return blob.public_url

# The save_temp_file function is no longer needed as we pass bytes in memory.