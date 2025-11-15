"""FastAPI application for querying stored HN stories."""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from hn_scraper.db import SessionLocal
from hn_scraper.models import Story

app = FastAPI(
    title="HN AI Scraper API",
    description="API for querying AI/ML-related Hacker News stories",
    version="1.0.0"
)


class StoryOut(BaseModel):
    """Pydantic model for Story output."""
    id: int
    hn_id: int
    title: str
    url: Optional[str]
    text: Optional[str]
    score: Optional[int]
    by: Optional[str]
    time: Optional[int]
    category: Optional[str]
    subcategory: Optional[str]
    summary: Optional[str]
    tags: Optional[str]
    relevance: Optional[float]
    is_processed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "name": "HN AI Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "GET /stories": "List all stories (with optional search and limit)",
            "GET /stories/{hn_id}": "Get a specific story by HN ID"
        }
    }


@app.get("/stories", response_model=List[StoryOut])
def list_stories(
    q: Optional[str] = Query(None, description="Search query for title/summary"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of stories to return")
):
    """
    List stories with optional search query.
    
    Args:
        q: Optional search query to filter by title or summary
        limit: Maximum number of stories to return (1-500)
        
    Returns:
        List of stories matching the criteria
    """
    db = SessionLocal()
    try:
        query = db.query(Story)
        
        if q:
            search_term = f"%{q}%"
            query = query.filter(
                (Story.title.ilike(search_term)) |
                (Story.summary.ilike(search_term)) |
                (Story.tags.ilike(search_term))
            )
        
        stories = query.order_by(Story.created_at.desc()).limit(limit).all()
        return stories
    finally:
        db.close()


@app.get("/stories/{hn_id}", response_model=StoryOut)
def get_story(hn_id: int):
    """
    Get a specific story by its HN ID.
    
    Args:
        hn_id: The Hacker News story ID
        
    Returns:
        Story details
        
    Raises:
        HTTPException: If story not found
    """
    db = SessionLocal()
    try:
        story = db.query(Story).filter(Story.hn_id == hn_id).first()
        if not story:
            raise HTTPException(status_code=404, detail=f"Story with HN ID {hn_id} not found")
        return story
    finally:
        db.close()
