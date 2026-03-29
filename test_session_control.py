import asyncio
from src.ai.providers import GoogleProvider
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

provider = GoogleProvider(api_key=api_key)
try:
    print(provider.extract_session_control("сел работать над проектом 1"))
except Exception as e:
    print("Error:", e)
