import requests
from agno.tools import tool
from pydantic import BaseModel, ValidationError
from typing import Any, Callable, Dict
import logging
from logger import init_logger

logger = init_logger(level=logging.DEBUG)

# ✅ Modèle Pydantic pour la réponse de l'API
class CryptoPriceEUR(BaseModel):
    EUR: float

@tool(show_result=True, stop_after_tool_call=True,
      cache_results=True, cache_dir="/tmp/agno_cache", cache_ttl=3600)
def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Hook function that wraps the tool execution"""
    print(f"About to call {function_name} with arguments: {arguments}")
    result = function_call(**arguments)
    print(f"Function call completed with result: {result}")
    return result

@tool(name="get_crypto_price",
      description="Obtenir le cours actuel en EUR d'une crypto-monnaie (ex: BTC, ETH).",
      show_result=True, 
      stop_after_tool_call=True,
    #   tool_hooks=[logger_hook],
      )
def get_crypto_price(symbol: str) -> str:
    """
    Trouve le cours actuel en EUR d'une crypto (ex: BTC, ETH).

    Args:
        symbol (str): Le symbole de la crypto-monnaie (ex: BTC, ETH).

    Returns:
        str: Le cours de la crypto-monnaie en euros en JSON, ou un message d'erreur.
    """
    logger.debug(f"Requête de prix pour la crypto : {symbol}")
    symbol = symbol.upper()
    url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=EUR&e=CCCAGG"
    logger.debug(f"URL utilisée : {url}")

    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        logger.debug(f"Données brutes reçues : {data}")

        # ✅ Validation via Pydantic
        parsed = CryptoPriceEUR(**data)
        response = f"Le cours de {symbol} est de {parsed.EUR:.2f} € "
        logger.debug(f"Réponse formatée : {response}")
        return response

    except ValidationError as ve:
        logger.error(f"Données inattendues : {ve}")
        return f"Données invalides reçues pour {symbol}"
    except requests.RequestException as e:
        logger.error(f"Erreur HTTP : {e}")
        return f"Erreur réseau pour {symbol} : {e}"
    except Exception as e:
        logger.error(f"Erreur inconnue : {e}")
        return f"Erreur inattendue pour {symbol} : {e}"
