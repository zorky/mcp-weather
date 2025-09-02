from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from typing import List, Optional

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.utils import fetch_rss_articles, filter_articles_by_keywords, summarize_article, read_opml

# Définition du schéma d’état
class RSSState(BaseModel):
    rss_urls: List[str]
    keywords: List[str]
    articles: Optional[List[dict]] = None
    filtered_articles: Optional[List[dict]] = None
    summaries: Optional[List[dict]] = None
    # summary: Optional[str] = None    

# Définis l'état de l'agent
def fetch_node(state: RSSState):
    articles = fetch_rss_articles(state.rss_urls)
    return state.model_copy(update={"articles": articles})
    # state_dict = state.dict()
    # articles = fetch_rss_articles(state_dict["rss_urls"])
    # state_dict["articles"] = articles
    # return RSSState(**state_dict)

def filter_node(state: RSSState):
    filtered = filter_articles_by_keywords(state.articles, state.keywords)
    return state.model_copy(update={"filtered_articles": filtered})
    

def summarize_node(state: RSSState):
    summaries = []
    for article in state.filtered_articles:
        summary = summarize_article(article["title"], article["summary"])
        summaries.append({
            "title": article["title"],
            "summary": summary,
            "link": article["link"]
        })
    return state.model_copy(update={"summaries": summaries})

def output_node(state: RSSState):
    for item in state.summaries:
        print(f"📰 {item['title']}\n📝 {item['summary']}\n🔗 {item['link']}\n")
    return state

def _make_graph():
    # Construction du graphe
    graph = StateGraph(RSSState)
    graph.add_node("fetch", RunnableLambda(fetch_node))
    graph.add_node("filter", RunnableLambda(filter_node))
    graph.add_node("summarize", RunnableLambda(summarize_node))
    graph.add_node("output", RunnableLambda(output_node))

    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "filter")
    graph.add_edge("filter", "summarize")
    graph.add_edge("summarize", "output")

    # Compile et exécute
    agent = graph.compile()
    return agent

def main():    
    # read_opml()
    agent = _make_graph()
    # Exemple d’état initial
    state = RSSState(
        rss_urls=[
            "https://cosmo-games.com/sujet/ia/feed/",
            "https://belowthemalt.com/feed/",
            "https://www.ajeetraina.com/rss/",
            # "https://www.lemonde.fr/rss/une.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
        ],
        # keywords=["intelligence artificielle", "climat", "cybersécurité"]
        keywords=["intelligence artificielle", "IA générative", "cybersécurité"]
    )

    agent.invoke(state)

if __name__=="__main__":
    main()
