import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def call_gemini(prompt: str) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    res = requests.post(GEMINI_URL, json=payload)
    if res.status_code == 200:
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error: {res.text}"
