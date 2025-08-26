from agno.models.ollama import Ollama
from ollama import Client
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from logger import init_logger
logger = init_logger(level=logging.DEBUG)

load_dotenv()
MODEL=os.getenv("LLM_MODEL", "llama3.1:8b")
LLM_API="http://localhost:11434/"
TEMPERATURE="0"

def get_ollama_model():
    ollama_sync_client = Client(
        host=LLM_API,
        headers={
            'temperature': TEMPERATURE
        }
    )
    ollama_model = Ollama(id=MODEL, provider="Ollama", client=ollama_sync_client)
    return ollama_model