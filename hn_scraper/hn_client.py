"""Hacker News API client functions."""
import requests
from typing import List, Optional, Dict


HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


def fetch_top_story_ids(limit: int = 100) -> List[int]:
    """
    Fetch the top story IDs from Hacker News.
    
    Args:
        limit: Maximum number of story IDs to return
        
    Returns:
        List of story IDs
    """
    url = f"{HN_API_BASE}/topstories.json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    story_ids = response.json()
    return story_ids[:limit]


def fetch_item(item_id: int) -> Optional[Dict]:
    """
    Fetch a single item (story, comment, etc.) from Hacker News.
    
    Args:
        item_id: The HN item ID to fetch
        
    Returns:
        Dictionary with item data or None if request fails
    """
    url = f"{HN_API_BASE}/item/{item_id}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None
