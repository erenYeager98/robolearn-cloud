# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from google.cloud import storage

from app.core.config import settings
from app.api.routers import ai_processing, audio, external_search, utility

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("--- Server Starting Up ---")
   

    # Initialize Cloud Storage client
    # No need to add to app.state if only used in file_service
    # But it's good practice to initialize clients at startup.
    app.state.storage_client = storage.Client()
    print("Google Cloud Storage client initialized.")

    print("--- Startup Complete ---")
    yield
    # --- Shutdown ---
    print("--- Server Shutting Down ---")


app = FastAPI(title="AI Learning Assistant API on GCP", lifespan=lifespan)

# Setup CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NOTE: We no longer mount a static directory. 
# File URLs will point directly to Google Cloud Storage.

# Include API routers
api_prefix = "/api"
app.include_router(ai_processing.router, prefix=api_prefix, tags=["AI Processing"])
app.include_router(audio.router, prefix=api_prefix, tags=["Audio"])
# app.include_router(emotion.router, prefix=api_prefix, tags=["Emotion"]) # Removed as emotion detection is now part of the prompt
app.include_router(external_search.router, prefix=api_prefix, tags=["External Search"])
app.include_router(utility.router, prefix=api_prefix, tags=["Utility"])


@app.get("/")
async def root():
    return {"message": "Welcome to the AI Learning Assistant API on GCP"}