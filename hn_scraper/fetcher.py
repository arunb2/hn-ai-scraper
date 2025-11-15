"""
Fetch and extract article content from URLs.
"""
import requests
from typing import Optional
from newspaper import Article
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def fetch_article_text(url: str) -> Optional[str]:
    """
    Fetch and extract the main text content from a URL.
    
    Uses newspaper3k as primary method with BeautifulSoup as fallback.
    
    Args:
        url: The URL to fetch content from
        
    Returns:
        Extracted text content, or None if extraction fails
    """
    try:
        # Try newspaper3k first
        article = Article(url)
        article.download()
        article.parse()
        
        if article.text and len(article.text.strip()) > 100:
            return article.text
    except Exception as e:
        print(f"Newspaper3k failed for {url}: {e}")
    
    # Fallback to BeautifulSoup
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.decompose()
        
        # Extract text from paragraphs
        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        if text and len(text.strip()) > 100:
            return text
            
    except Exception as e:
        print(f"BeautifulSoup fallback failed for {url}: {e}")
    
    return None
