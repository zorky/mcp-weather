# from langchain.llms import Ollama
# from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOpenAI
import feedparser
import os

MODEL=os.getenv("MODEL_NAME", "mistral")
LLM_API=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
LLM_TEMPERATURE=os.getenv("LLM_TEMPERATURE", '0.3')

# Initialise ton modèle local
# llm = Ollama(model="mistral")  # Ou "llama3", "gemma", etc.
llm = ChatOpenAI(
    temperature=LLM_TEMPERATURE,
    model=MODEL,
    openai_api_base=LLM_API,
    openai_api_key="dummy-key-ollama",
)

def summarize_article(title, content):
    prompt = f"""Tu es un journaliste expert. Résume cet article en 3 phrases claires et concises.
Titre : {title}
Contenu : {content}
"""
    return llm.invoke(prompt)

def fetch_rss_articles(rss_urls):
    feeds = [feedparser.parse(url) for url in rss_urls]
    articles = []
    for feed in feeds:
        for entry in feed.entries:
            articles.append({
                "title": entry.title,
                "summary": entry.summary,
                "link": entry.link
            })
    return articles

def filter_articles_by_keywords(articles, keywords):
    filtered = []
    for article in articles:
        if any(k.lower() in article["title"].lower() or k.lower() in article["summary"].lower() for k in keywords):
            filtered.append(article)
    return filtered

