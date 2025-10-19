# app/services/ai_service.py

import google.generativeai as genai
import httpx
from app.core.config import settings
import io
from PIL import Image # For processing image data
import json

# Configure the client library with your API key
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    # This will cause subsequent calls to fail, which is intended if the key is missing.

# Use a compatible model name for the Google AI API
GEMINI_MODEL_ID = "gemini-flash-latest" # <-- Correct and complete identifier

# async def generate_research_response_with_gemini(question: str, emotion: str, level: int) -> str:
#     """Generates a response using the Google AI Gemini API."""
    
#     if emotion.lower() in ["neutral", "sad"]:
#         emotion_instruction = "The user is in a calm or low mood, so explain the topic thoroughly but in a gentle and easy-to-follow manner."
#     elif emotion.lower() in ["happy", "excited", "joy"]:
#         emotion_instruction = "The user is in a good mood, so you can explain the topic with enthusiasm, depth, and engaging details."
#     else:
#         emotion_instruction = "Adjust your response tone to suit the user's emotion. Prioritize clarity and depth."

#     system_prompt = (
#         "You are a knowledgeable, friendly teacher who explains topics thoroughly.\n"
#         "Always respond with a detailed, structured explanation of about 1000-1200 words.\n"
#         "Break the content into clear sections or paragraphs, and use examples when appropriate.\n"
#         "If the query is vague, ask for clarification before explaining.\n"
#         f"{emotion_instruction}\n"
#         "Your tone should remain helpful, supportive, engaging, and educational."
#     )
    
#     prompt = f"Query: {question}\nEmotion: {emotion}"
            
#     model = genai.GenerativeModel(
#         GEMINI_MODEL_ID,
#         system_instruction=system_prompt
#     )
    
#     response = await model.generate_content_async(
#         prompt,
#         generation_config=genai.types.GenerationConfig(
#             temperature=0.7,
#             top_p=0.9,
#             max_output_tokens=4096,
#         )
#     )
    
#     return response.text

import google.generativeai as genai

# Assume genai is configured with your API key
# genai.configure(api_key="YOUR_API_KEY")
# GEMINI_MODEL_ID = "gemini-1.5-flash" # or your preferred model

async def generate_research_response_with_gemini(question: str, emotion: str, level: int) -> str:
    """Generates a response using the Google AI Gemini API."""

    # --- Logic for handling the 'emotion' parameter ---
    if emotion.lower() in ["neutral", "sad"]:
        emotion_instruction = "The user is in a calm or low mood, so explain the topic thoroughly but in a gentle and easy-to-follow manner."
    elif emotion.lower() in ["happy", "excited", "joy"]:
        emotion_instruction = "The user is in a good mood, so you can explain the topic with enthusiasm, depth, and engaging details."
    else:
        emotion_instruction = "Adjust your response tone to suit the user's emotion. Prioritize clarity and depth."

    # --- Logic for handling the 'level' parameter ---
    if level == 1:
        level_instruction = "Explain the topic in a beginner-friendly way. Avoid jargon and use simple analogies."
        word_count_instruction = "Your explanation should be about 250-400 words."
    elif level == 2:
        level_instruction = "Explain the topic for an intermediate learner. You can assume some basic knowledge but should still define key terms."
        word_count_instruction = "Your explanation should be about 450-600 words."
    else: # Default to level 3 for advanced or any other value
        level_instruction = "Explain the topic thoroughly for an advanced learner. Provide in-depth details, nuances, and complex examples where appropriate."
        word_count_instruction = "Your explanation should be about 800-1000 words."

    # --- Dynamically build the system prompt ---
    system_prompt = (
        "You are a knowledgeable, friendly teacher who explains topics thoroughly.\n"
        f"{word_count_instruction}\n"
        f"{level_instruction}\n"
        "Break the content into clear sections or paragraphs, and use examples when appropriate.\n"
        "If the query is vague, ask for clarification before explaining.\n"
        f"{emotion_instruction}\n"
        "Your tone should remain helpful, supportive, engaging, and educational."
    )
    
    prompt = f"Query: {question}\nEmotion: {emotion}\nLevel: {level}"
            
    model = genai.GenerativeModel(
        GEMINI_MODEL_ID,
        system_instruction=system_prompt
    )
    
    response = await model.generate_content_async(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.9,
            max_output_tokens=4096,
        )
    )
    
    return response.text

async def generate_summary_with_gemini(content: str) -> str:
    """Generates a summary using the Google AI Gemini API."""

    system_prompt = (
        "You are an expert academic assistant.\nSummarize the given content in about 50 words.\n"
        "The summary must start with: 'This article states that'.\n"
        "Write clearly and professionally. Do not add notes, opinions, or extra commentary, and do not use markdown formatting like bold text."
    )
    
    model = genai.GenerativeModel(
        GEMINI_MODEL_ID,
        system_instruction=system_prompt
    )

    response = await model.generate_content_async(
        f"Content to summarize: {content.strip()}",
        generation_config=genai.types.GenerationConfig(
            temperature=0.2,
            max_output_tokens=200,
        )
    )

    summary = response.text.strip()
    if not summary.lower().startswith("this article states that"):
        summary = f"This article states that {summary}"
        
    return summary

async def analyze_image_with_gemini(image_bytes: bytes, mime_type: str) -> str:
    """Analyzes an image using the Google AI Gemini API."""
    
    instruction = "Answer the question shown in the image."
    
    # The Google AI SDK works well with PIL images
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise ValueError(f"Could not process image bytes: {e}")

    model = genai.GenerativeModel(GEMINI_MODEL_ID)
    
    response = await model.generate_content_async(
        [instruction, image],
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            top_p=1.0,
            max_output_tokens=2048,
        )
    )
    
    return response.text

async def generate_image_urls(question: str, emotion: str) -> list[str]:
    """
    Generates image URLs by getting search keywords from Gemini and then fetching
    images using the Serper API.
    """
    try:
        # 1. Generate Keywords with Gemini
        model = genai.GenerativeModel(GEMINI_MODEL_ID)
        
        prompt = (
            "You are an assistant that only outputs 3 to 5 short, comma-separated keywords for an image search. "
            "Do not use numbered lists, explanations, or any other text. Just return the keywords.\n"
            f"Query: {question}\n"
            f"Emotion: {emotion}"
        )
        
        response = await model.generate_content_async(prompt)
        keywords = response.text.strip()
        print(f"✨ Generated Keywords: {keywords}")

        # 2. Fetch Image URLs with Serper API using httpx
        url = "https://google.serper.dev/images"
        payload = json.dumps({"q": keywords})
        headers = {
            'X-API-KEY': settings.SERPER_API_KEY,
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            api_response = await client.post(url, headers=headers, content=payload)
            api_response.raise_for_status()
            data = api_response.json()

        # 3. Extract top 10 image URLs
        image_urls = [item["imageUrl"] for item in data.get("images", [])[:10]]
        return image_urls

    except httpx.HTTPStatusError as http_err:
        print(f"HTTP error occurred while calling Serper API: {http_err}")
        return []
    except Exception as e:
        print(f"An error occurred in generate_image_urls: {e}")
        return []