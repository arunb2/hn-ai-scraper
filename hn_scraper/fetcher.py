"""Article content fetcher using newspaper3k with BeautifulSoup fallback."""
import requests
from bs4 import BeautifulSoup
from typing import Optional
import logging

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def fetch_article_text(url: str) -> Optional[str]:
    """
    Fetch article text from a URL using newspaper3k, with BeautifulSoup fallback.
    
    Args:
        url: The article URL to fetch
        
    Returns:
        Article text or None if fetching fails
    """
    if not url:
        return None
    
    # Try newspaper3k first
    if NEWSPAPER_AVAILABLE:
        try:
            article = Article(url)
            article.download()
            article.parse()
            if article.text and len(article.text.strip()) > 100:
                return article.text
        except Exception as e:
            logger.debug(f"newspaper3k failed for {url}: {e}")
    
    # Fallback to requests + BeautifulSoup
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text from paragraphs
        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text() for p in paragraphs])
        
        if text and len(text.strip()) > 100:
            return text.strip()
            
    except Exception as e:
        logger.debug(f"BeautifulSoup fallback failed for {url}: {e}")
    
    return None
