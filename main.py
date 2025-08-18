"""
Application principale pour le serveur FastAPI qui gère les requêtes de l'agent
ask + tools <--> Ollama LLM
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict

import logging
from logger import init_logger

from agent.agent import get_agent_team

app = FastAPI()
logger = init_logger(level=logging.DEBUG)

@app.get("/ask")
async def ask_agent(question: str):
    # response = agent.print_response(question, stream=False, show_full_reason=True)
    response = get_agent_team().run(question)
    logger.debug(f"** ask_agent : {response.content}")
    logger.debug(f"** ask_agent reasoning : {response.reasoning_content}")
    return {"response": response.content}
