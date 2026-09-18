from google import genai
from google.genai.errors import APIError
from google.genai import types
import requests
import time
import tempfile
import os
import logging
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)

DEFAULT_MODEL = "gemini-flash-lite-latest"

SYSTEM_INSTRUCTION = "You are Bridges AI, an advanced, precise, and helpful AI assistant."

def validate_key(api_key):
    if not api_key or not isinstance(api_key, str):
        return False, "Invalid API Key."    
    try:
        client = genai.Client(api_key=api_key.strip())
        next(iter(client.models.list(config={"page_size": 1})), None)
        return True, "API Key successfully connected."
    except APIError:
        return False, "Invalid API Key."
    except Exception:
        return False, "Execution error. Please try again later."


def send_message(api_key, history, user_text):
    try:
        client = genai.Client(api_key=api_key.strip())
        contents = []
        for role, text in history:
            contents.append(types.Content(role=role,parts=[types.Part.from_text(text=text)]))
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_text)]))
        config = types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=contents,
            config=config
        )
        if not response.text:
            return False, "Response was blocked by safety filters or empty."
        return True, response.text
    except APIError as e:
        if e.code == 429:
            return False, "Quota exceeded. Please wait a moment."
        return False, "AI service error. Please try again."
    except Exception:
        return False, "Connection error. Please try again later."