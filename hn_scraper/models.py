from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Story(Base):
    """SQLAlchemy model for storing Hacker News stories."""
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    hn_id = Column(Integer, unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(2000))
    text = Column(Text)
    score = Column(Integer)
    by = Column(String(200))
    time = Column(Integer)
    category = Column(String(200))
    subcategory = Column(String(200))
    summary = Column(Text)
    tags = Column(String(500))
    relevance = Column(Float)
    is_processed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
