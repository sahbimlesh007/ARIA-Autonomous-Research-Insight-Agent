from dotenv import load_dotenv

load_dotenv()


from langchain_mistralai import ChatMistralAI
from tavily import TavilyClient
from langchain.tools import tool

import requests
from bs4 import BeautifulSoup

from rich import print
import os

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def webSearch(query: str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = tavily.search(query=query, max_results=5)

    out = []

    for r in results["results"]:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\Snippet: {r['content'][:300]}\n"
        )
    return "\n-------\n".join(out)


@tool
def urlScrapper(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""

    try:
        response = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        return soup.get_text(separator=" ", strip=True)[:500]

    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
