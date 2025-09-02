from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from typing import List, Optional
from langchain_community.chat_models import ChatOpenAI
import feedparser
import os
import opml

# =========================
# Configuration du modèle
# =========================
MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_API = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

llm = ChatOpenAI(
    temperature=LLM_TEMPERATURE,
    model=MODEL,
    openai_api_base=LLM_API,
    openai_api_key="dummy-key-ollama",
)

# =========================
# Fonctions utilitaires
# =========================
def log_step(message: str):
    print(f"\n🔹 {message}")

def summarize_article(title, content):
    prompt = f"""Tu es un journaliste expert. Résume en français cet article en 3 phrases claires et concises.
Titre : {title}
Contenu : {content}
"""
    result = llm.invoke(prompt)
    return result.content.strip() if hasattr(result, "content") else str(result).strip()

def fetch_rss_articles(rss_urls):
    articles = []
    for url in rss_urls:
        log_step(f"Lecture du flux RSS : {url}")
        feed = feedparser.parse(url)
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

def read_opml():
    o = opml.parse('my.opml')
    for x in o:
        print(x.text)        
        for y in x:
            if y.type == "rss":            
                print(y.xmlUrl)

# =========================
# Définition de l’état
# =========================
class RSSState(BaseModel):
    rss_urls: List[str]
    keywords: List[str]
    articles: Optional[List[dict]] = None
    filtered_articles: Optional[List[dict]] = None
    summaries: Optional[List[dict]] = None    

# =========================
# Nœuds du graphe
# =========================
def fetch_node(state: RSSState):
    log_step("📥 Récupération des articles...")
    articles = fetch_rss_articles(state.rss_urls)
    print(f"   → {len(articles)} articles récupérés")
    return state.model_copy(update={"articles": articles})

def filter_node(state: RSSState):
    log_step("🔍 Filtrage des articles par mots-clés...")
    filtered = filter_articles_by_keywords(state.articles, state.keywords)
    print(f"   → {len(filtered)} articles correspondent aux mots-clés")
    return state.model_copy(update={"filtered_articles": filtered})

def summarize_node(state: RSSState):
    log_step("✏️  Résumé des articles filtrés...")
    summaries = []
    for i, article in enumerate(state.filtered_articles, start=1):
        print(f"   → Résumé {i}/{len(state.filtered_articles)} : {article['title']}")
        summary_text = summarize_article(article["title"], article["summary"])
        summaries.append({
            "title": article["title"],
            "summary": summary_text,
            "link": article["link"]
        })
    return state.model_copy(update={"summaries": summaries})

def output_node(state: RSSState):
    log_step("📄 Affichage des résultats finaux")
    for item in state.summaries:
        print(f"\n📰 {item['title']}\n📝 {item['summary']}\n🔗 {item['link']}")
    return state

# =========================
# Construction du graphe
# =========================
def _make_graph():
    graph = StateGraph(RSSState)
    graph.add_node("fetch", RunnableLambda(fetch_node))
    graph.add_node("filter", RunnableLambda(filter_node))
    graph.add_node("summarize", RunnableLambda(summarize_node))
    graph.add_node("output", RunnableLambda(output_node))

    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "filter")
    graph.add_edge("filter", "summarize")
    graph.add_edge("summarize", "output")

    return graph.compile()

# =========================
# Main
# =========================
def main():
    agent = _make_graph()
    state = RSSState(
        rss_urls=[
            "https://cosmo-games.com/sujet/ia/feed/",
            "https://belowthemalt.com/feed/",
            "https://www.ajeetraina.com/rss/",
            "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
        ],
        keywords=["intelligence artificielle", "IA générative", "cybersécurité"]
    )
    agent.invoke(state)

if __name__ == "__main__":
    main()
