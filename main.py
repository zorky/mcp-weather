"""
Application principale pour le serveur FastAPI qui gère les requêtes de l'agent
ask + tools <--> Ollama LLM
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict

import logging
from logger import init_logger

from agent.agent import agent
from agent.agent_executor import create_hybrid_agent

from tools.weather_tools import get_weather

app = FastAPI()
logger = init_logger(level=logging.DEBUG)

@app.get("/ask")
async def ask_agent(question: str):
    # question_enhancement = f"{question}\n\nRéponds en français en Markdown."
    # return {"response": agent.run(question_enhancement)}
    return {"response": agent.run(question)}

@app.get("/ask_hybrid")
async def ask_hybrid(question: str):
    logger.debug(f"Entering new AgentExecutor chain...with question : {question}")
    agent = create_hybrid_agent()
    response = agent.invoke({"input": question})
    return {"response": response["output"]}

@app.get("/mcp/tools")
async def list_tools():
    # MCP veut un tableau de descriptions JSON
    import json
    with open("mcp_server/tools.json") as f:
        return JSONResponse(content=json.load(f))

class ToolCallRequest(BaseModel):
    name: str
    parameters: Dict

@app.post("/mcp/tool_call")
async def call_tool(request: ToolCallRequest):
    tool_name = request.name
    params = request.parameters
    if tool_name == "get_weather":
        result = get_weather(params.get("city", ""))
        return {"result": result}
    elif tool_name == "get_coordinates_openstreetmap":
        from mcp_server.geo_tools import get_coordinates_openstreetmap
        result = get_coordinates_openstreetmap(params.get("city", ""))
        return {"result": result}
    else:
        return JSONResponse(status_code=400, content={"error": "Tool not found"})

"""
> Entering new AgentExecutor chain...
A weather-related question! Let's get started.

Thought: To find out the weather at Paris, I need to get the current weather conditions. Since we have a tool for getting weather forecasts, let's use that.

Action: get_weather
Action Input: Paris/mnt/d/wutemp/p8/workspace/mcp-weather/mcp_server/weather_tools.py:12: LangChainDeprecationWarning: The method `BaseTool.__call__` was deprecated in langchain-core 0.1.47 and will be removed in 1.0. Use :meth:`~invoke` instead.
  lat, lon = get_coordinates_openstreetmap(city)
Coordonnées de Paris : latitude = 48.8534951, longitude = 2.3483915
Météo pour Paris : Prévisions météo pour les 3 prochains jours :
- 2025-08-01 : 17.9°C → 23.4°C, pluie : 2.4 mm
- 2025-08-02 : 15.9°C → 21.3°C, pluie : 0.0 mm
- 2025-08-03 : 14.4°C → 23.8°C, pluie : 0.0 mm

Observation: Prévisions météo pour les 3 prochains jours :
- 2025-08-01 : 17.9°C → 23.4°C, pluie : 2.4 mm
- 2025-08-02 : 15.9°C → 21.3°C, pluie : 0.0 mm
- 2025-08-03 : 14.4°C → 23.8°C, pluie : 0.0 mm

Thought:Thought: Now that I have the weather forecast for Paris, I can use this information to answer the original question.

Action: None needed, just using the observation from before!

Observation (again): Prévisions météo pour les 3 prochains jours :
- 2025-08-01 : 17.9°C → 23.4°C, pluie : 2.4 mm
- 2025-08-02 : 15.9°C → 21.3°C, pluie : 0.0 mm
- 2025-08-03 : 14.4°C → 23.8°C, pluie : 0.0 mm

Thought: I now know the final answer!

Final Answer: Le temps à Paris est prévu pour les 3 prochains jours comme suit :
- 2025-08-01 : 17.9°C → 23.4°C, avec une chance de pluie (2.4 mm)
- 2025-08-02 : 15.9°C → 21.3°C, sans pluie
- 2025-08-03 : 14.4°C → 23.8°C, sans pluie

> Finished chain.

Final Answer: La météo des 3 prochains jours à Bordeaux, France est :
- 2025-08-01 : 16.1°C → 25.8°C, pluie : 0.0 mm
- 2025-08-02 : 17.2°C → 24.5°C, pluie : 0.0 mm
- 2025-08-03 : 15.7°C → 27.8°C, pluie : 0.0 mm

"""