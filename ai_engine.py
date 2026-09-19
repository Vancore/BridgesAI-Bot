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

SYSTEM_INSTRUCTION = (
    "You are Bridges AI, an advanced, precise, and helpful AI assistant. "
    "Be concise and direct by default. Avoid conversational filler, introductory pleasantries, "
    "and restating the user's question. Provide expanded, in-depth explanations only when explicitly "
    "asked or when the complexity of the topic strictly requires it."
)

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
    text = (user_text or "").strip()
    if not text:
        return False, "Prompt cannot be empty."
    try:
        client = genai.Client(api_key=api_key.strip())
        contents = []
        expected_role = "user"
        for role, h_text in history:
            h_clean = (h_text or "").strip()
            if not h_clean:
                continue
            if role == expected_role:
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=h_clean)]))
                expected_role = "model" if expected_role == "user" else "user"
        if contents and expected_role == "model":
            contents.pop()
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=text)]))
        config = types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=contents,
            config=config
        )
        try:
            res_text = response.text
        except Exception:
            res_text = None

        if not res_text:
            return False, "Response was blocked by safety filters or empty."
        return True, res_text
    except APIError as e:
        if e.code == 429:
            return False, "Quota exceeded. Please wait a moment."
        return False, f"AI service error: {e.message or 'Please try again.'}"
    except Exception:
        return False, "Connection error. Please try again later."
