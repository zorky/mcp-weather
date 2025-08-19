import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from ollama import Client

from agno.models.ollama import Ollama
from agno.agent import Agent, RunResponse
# from agno.tools.reasoning import ReasoningTools
# from agno.utils.pprint import pprint_run_response
from rich.pretty import pprint

from tools.crypto_price import get_crypto_price
# from agent.agent import _get_agent


load_dotenv()
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/")
LLM_TEMPERATURE = os.getenv("LLM_TEMPERATURE", '0')  # 0 : déterministe et précis, 0.3 : un peu plus créatif, etc

def _get_ollama_model():
    ollama_sync_client = Client(
        host=OLLAMA_BASE_URL,
        headers={
            'temperature': LLM_TEMPERATURE,
            'seed': '1234567890'
        }
    )
    ollama_model = Ollama(id=LLM_MODEL, provider="Ollama", client=ollama_sync_client)
    return ollama_model

def _print_metrics(agent: Agent):
    # Print metrics per message
    if agent.run_response.messages:
        for message in agent.run_response.messages:
            if message.role == "assistant":
                if message.content:
                    print(f"Message: {message.content}")
                elif message.tool_calls:
                    print(f"Tool calls: {message.tool_calls}")
                print("---" * 5, "Metrics", "---" * 5)
                pprint(message.metrics)
                print("---" * 20)

    # Print the aggregated metrics for the whole run
    print("---" * 5, "Collected Metrics", "---" * 5)
    pprint(agent.run_response.metrics)
    # Print the aggregated metrics for the whole session
    print("---" * 5, "Session Metrics", "---" * 5)
    pprint(agent.session_metrics)

def _get_agent(name: str, role: str, tools: list, instructions: str | list[str], /) -> Agent:
    return Agent(
        name=name,
        role=role,
        model=_get_ollama_model(),
        tools=tools,
        instructions=instructions,
        show_tool_calls=False,
        # use_json_mode=True,
        markdown=True,
    )

if __name__ == "__main__":
    print(f"LLM_MODEL: {LLM_MODEL} {OLLAMA_BASE_URL} {LLM_TEMPERATURE}")
    crypto_agent = _get_agent("Expert cours de crypto monnaies",
                                     "Donner le cours de crypto monnaies",
                                [get_crypto_price],
                                      # [get_crypto_price, ReasoningTools(add_instructions=True)],
                                      "Réponds uniquement sur le cours d'un ou plusieurs cryptomonnaies.")
    # crypto_agent.print_response("Quel est le cours du BTC et de l'ETH ?", stream=False, show_full_reason=True)
    crypto_agent.print_response(
        "Quel est le cours du BTC et de l'ETH ?", stream=False
    )
    _print_metrics(crypto_agent)
    # response: RunResponse = crypto_agent.run("Quel est le cours du BTC et de l'ETH ?")
    # print(f"** response : {response.content}")
    # pprint_run_response(response, markdown=True)

