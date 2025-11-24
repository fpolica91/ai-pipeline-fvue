from dotenv import load_dotenv
import os

load_dotenv()

GROK_API_KEY = os.getenv("OPENAI_API_KEY")

CACHE_DIR='./cache'