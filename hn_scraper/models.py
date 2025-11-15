"""
SQLAlchemy models for the HN scraper database.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Story(Base):
    """Model for storing Hacker News stories with classification metadata."""
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    hn_id = Column(Integer, unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(2000), nullable=True)
    text = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    by = Column(String(100), nullable=True)
    time = Column(Integer, nullable=True)
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)
    relevance = Column(Float, nullable=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Story(hn_id={self.hn_id}, title='{self.title[:50]}...')>"
