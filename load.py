import os
import databases
from dotenv import load_dotenv

load_dotenv()

token_bot = os.environ.get("token_bot")
api_id = os.environ.get("api_id")
api_hash = os.environ.get("api_hash")
