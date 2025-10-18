# app/services/audio_service.py

from google.cloud import speech
from google.cloud import texttospeech
import asyncio

async def transcribe_audio_gcp(audio_content: bytes) -> str:
    """Transcribes audio using Google Cloud Speech-to-Text."""
    client = speech.SpeechAsyncClient()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        # encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS, # Or let it auto-detect
        sample_rate_hertz=48000, # Common for webm
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    response = await client.recognize(config=config, audio=audio)

    if response.results:
        return response.results[0].alternatives[0].transcript
    return ""


async def generate_tts_audio_gcp(text: str) -> bytes:
    """Generates speech from text using Google Cloud Text-to-Speech."""
    client = texttospeech.TextToSpeechAsyncClient()
    
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", 
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = await client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    return response.audio_content