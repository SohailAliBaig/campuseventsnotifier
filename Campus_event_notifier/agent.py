import os
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai
import traceback

def _get_gemini_key():
    # Try loading from both the project root and package .env if necessary
    project_root = Path(__file__).parent.parent
    pkg_env = Path(__file__).parent / ".env"
    root_env = project_root / ".env"
    # Load root first; only use a key if it's non-empty after stripping
    load_dotenv(dotenv_path=root_env)
    key = os.getenv("GEMINI_API_KEY")
    if key:
        k = key.strip('"').strip("'").strip()
        if k:
            return k

    # If root didn't provide a usable key, try package .env
    load_dotenv(dotenv_path=pkg_env)
    key = os.getenv("GEMINI_API_KEY")
    if key:
        k = key.strip('"').strip("'").strip()
        if k:
            return k

    return None


def ask_agentic_ai(prompt: str) -> str:
    """Send a prompt to Google Gemini AI and return the response.

    Returns a friendly error message if the API key is missing or the call fails.
    """
    GEMINI_KEY = _get_gemini_key()
    if not GEMINI_KEY:
        return "Error: GEMINI_API_KEY not configured on the server. Please set GEMINI_API_KEY in your .env."

    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        if hasattr(response, "text"):
            return response.text.strip()
        return str(response).strip()
    except Exception as e:
        print("⚠️ Gemini call failure:")
        traceback.print_exc()
        return f"Error: Gemini call failed: {e}"
