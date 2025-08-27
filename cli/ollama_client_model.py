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

# tools Ollama https://ollama.com/blog/tool-support
MODEL=os.getenv("LLM_MODEL", "llama3.1:8b")
# MODEL="mistral" # Mistral-7B-Instruct-v0.3 sur archi llama GGUF V3 Q4_K - Medium
# MODEL="mistral:7b-instruct-q8_0" # no tools !
# MODEL="llama3:8b-instruct-q4_K_M" # no tools !

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