from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_MODEL_NAME = "gemini-3.5-flash-lite"

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

print(os.getenv("GENAI_API_KEY"))