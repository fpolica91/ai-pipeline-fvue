from dotenv import load_dotenv
import os

load_dotenv()

GROK_API_KEY = os.getenv("OPENAI_API_KEY")

CACHE_DIR='./cache'

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "database.db")