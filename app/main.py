"""
FastAPI application for querying stored HN stories.
"""
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from hn_scraper.db import SessionLocal
from hn_scraper.models import Story

app = FastAPI(
    title="HN AI Scraper API",
    description="API for querying Hacker News stories classified by AI",
    version="1.0.0"
)


# Pydantic model for response
class StoryOut(BaseModel):
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
    created_at: Optional[str]
    
    class Config:
        from_attributes = True  # Replaces orm_mode in Pydantic v2


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "HN AI Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "stories": "/stories",
            "story_by_id": "/stories/{hn_id}",
            "docs": "/docs"
        }
    }


@app.get("/stories", response_model=List[StoryOut])
def list_stories(
    q: Optional[str] = Query(None, description="Search query for title, category, or tags"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of stories to return"),
    db: Session = Depends(get_db)
):
    """
    List stored stories with optional search and limit.
    
    Args:
        q: Optional search query (searches title, category, subcategory, and tags)
        limit: Maximum number of stories to return (1-500)
        db: Database session
        
    Returns:
        List of stories
    """
    query = db.query(Story).order_by(Story.created_at.desc())
    
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            (Story.title.ilike(search_term)) |
            (Story.category.ilike(search_term)) |
            (Story.subcategory.ilike(search_term)) |
            (Story.tags.ilike(search_term))
        )
    
    stories = query.limit(limit).all()
    return stories


@app.get("/stories/{hn_id}", response_model=StoryOut)
def get_story(hn_id: int, db: Session = Depends(get_db)):
    """
    Get a specific story by its Hacker News ID.
    
    Args:
        hn_id: Hacker News story ID
        db: Database session
        
    Returns:
        Story details
        
    Raises:
        HTTPException: If story not found
    """
    story = db.query(Story).filter(Story.hn_id == hn_id).first()
    if not story:
        raise HTTPException(status_code=404, detail=f"Story with hn_id {hn_id} not found")
    return story


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
