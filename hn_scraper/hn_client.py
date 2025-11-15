"""
Client for interacting with the Hacker News Firebase API.
"""
import requests
from typing import Optional, List, Dict

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


def fetch_top_story_ids(limit: int = 100) -> List[int]:
    """
    Fetch the IDs of the top stories from Hacker News.
    
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
    Fetch a specific item (story, comment, etc.) from Hacker News.
    
    Args:
        item_id: The ID of the item to fetch
        
    Returns:
        Dictionary containing item data, or None if not found
    """
    url = f"{HN_API_BASE}/item/{item_id}.json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
