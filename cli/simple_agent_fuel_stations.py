"""
Building an AI Agent with Agno: A Step-by-Step Guide
https://ai.plainenglish.io/building-an-ai-agent-with-agno-a-step-by-step-guide-13542b2a5fb6
https://github.com/Bavalpreet/AI-Agents/tree/main/agno

API : https://developers.oxylabs.io/scraping-solutions/web-scraper-api/targets/google/search/local-search
Free trial : https://dashboard.oxylabs.io/en/overview/scraper/buy-now

curl ''https://realtime.oxylabs.io/v1/queries'' --user 'zorky_magBl:***************' -H 'Content-Type: application/json' -d '{"source": "google_search", "query": "adidas", "geo_location": "California,United States", "parse": true}'
"""

import os
import requests
from agno.agent import Agent
# from agno.models.openai import OpenAIChat

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from cli.ollama_client_model import get_ollama_model

import logging
from logger import init_logger
logger = init_logger(level=logging.DEBUG)

# Define custom Oxylabs tool
class FuelStationSearchTool:
    """
    A tool for searching fuel stations using the Oxylabs API.
    https://developers.oxylabs.io/scraping-solutions/web-scraper-api/targets/google/search/local-search
    """
    USERNAME=os.getenv('LOGIN')    
    PASSWORD=os.getenv('PASSWORD')
    
    URL="https://realtime.oxylabs.io/v1/queries"

    def __init__(self):
        self.name = "FuelStationSearchTool"
        self.description = "Fetches nearby fuel stations using Oxylabs Real-Time API."

    def run(self, location_query, pages=1):    
        logger.debug(f"usr / pwd : {self.USERNAME} {self.PASSWORD}")
        payload = {
            'source': 'google_maps',
            'domain': 'fr',
            'query': f'stations services à {location_query}',
            'pages': pages,
        }
        logger.debug(f"Oxylabs API payload: {payload} with {self.URL}")
        response = requests.post(
            self.URL,
            auth=(self.USERNAME, self.PASSWORD),
            json=payload,
        )

        if response.status_code != 200:
            return f"API Error: {response.status_code}, {response.text}"

        data = response.json()

        stations_info = []        
        logger.debug(f"results : {data.get('results')[:1]}")
        for result in data.get('results', [])[:5]:
            title = result.get('title', 'No Name')
            address = result.get('address', 'Address Unavailable')
            rating = result.get('rating', 'Rating Unavailable')
            station_data = f"{title} - {address} (Rating: {rating})"
            stations_info.append(station_data)
            logger.debug(f"Oxylabs API response data: {station_data}")

        if not stations_info:
            return "No nearby fuel stations found."

        return "\n".join(stations_info)

# Initialize Agno agent
agent = Agent(
    # model=OpenAIChat(id="gpt-4o"),    
    model=get_ollama_model(),
    description="An intelligent logistics assistant helping drivers find nearby services.",
    instructions=[
        "Use FuelStationSearchTool for queries about nearby fuel stations.",
        "List fuel stations clearly with names, addresses, and ratings.",
        "Answer in french only"
    ],
    markdown=True,
    show_tool_calls=True,    
    tool_call_limit=5,
    debug_mode=True,
    tools=[FuelStationSearchTool()]
)

# Main execution
if __name__ == "__main__":
    fuel = FuelStationSearchTool()
    fuel.run(location_query="Noisy-le-Grand, France")

    # default_location="Noisy-le-Grand, France"
    # location = input(f"Entrez votre localisation (ou appuyez sur Entrée pour la question par défaut '{default_location}') : ") or default_location    
    # location_query = location
    # agent.print_response(location_query)