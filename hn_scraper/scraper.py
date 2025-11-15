"""Main scraper orchestrator for HN AI scraper."""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

from hn_scraper.db import SessionLocal, init_db
from hn_scraper.models import Story
from hn_scraper.hn_client import fetch_top_story_ids, fetch_item
from hn_scraper.fetcher import fetch_article_text
from hn_scraper.processor import classify_and_summarize

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

HN_MAX_STORIES = int(os.getenv("HN_MAX_STORIES", "100"))
SCRAPE_MIN_SCORE = int(os.getenv("SCRAPE_MIN_SCORE", "10"))
KEYWORDS = [k.strip().lower() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]

MAX_TEXT_LENGTH = 20000


def matches_keywords(title: str, url: Optional[str]) -> bool:
    """Check if title or URL contains any of the configured keywords."""
    if not KEYWORDS:
        return True
    
    text_to_check = f"{title} {url or ''}".lower()
    return any(keyword in text_to_check for keyword in KEYWORDS)


def run_once(limit: Optional[int] = None):
    """
    Run the scraper once to fetch, process, and store HN stories.
    
    Args:
        limit: Optional limit on number of stories to process (overrides HN_MAX_STORIES)
    """
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Fetch top story IDs
    max_stories = limit or HN_MAX_STORIES
    logger.info(f"Fetching top {max_stories} story IDs from HN")
    
    try:
        story_ids = fetch_top_story_ids(limit=max_stories)
        logger.info(f"Retrieved {len(story_ids)} story IDs")
    except Exception as e:
        logger.error(f"Failed to fetch story IDs: {e}")
        return
    
    # Process each story
    processed_count = 0
    saved_count = 0
    
    for idx, story_id in enumerate(story_ids, 1):
        logger.info(f"Processing story {idx}/{len(story_ids)}: ID {story_id}")
        
        try:
            # Fetch item details
            item = fetch_item(story_id)
            if not item:
                logger.warning(f"Failed to fetch item {story_id}")
                continue
            
            # Skip non-story types
            if item.get("type") != "story":
                logger.info(f"Skipping non-story type: {item.get('type')}")
                continue
            
            # Check minimum score
            score = item.get("score", 0)
            if score < SCRAPE_MIN_SCORE:
                logger.info(f"Skipping story with score {score} (below minimum {SCRAPE_MIN_SCORE})")
                continue
            
            # Check if already in database
            db = SessionLocal()
            try:
                existing = db.query(Story).filter(Story.hn_id == story_id).first()
                if existing:
                    logger.info(f"Story {story_id} already in database, skipping")
                    db.close()
                    continue
            finally:
                db.close()
            
            title = item.get("title", "")
            url = item.get("url")
            
            # Prefilter by keywords
            if not matches_keywords(title, url) and score < 50:
                logger.info(f"Story doesn't match keywords and score < 50, skipping")
                continue
            
            # Fetch article text if URL present
            article_text = None
            if url:
                logger.info(f"Fetching article text from {url}")
                article_text = fetch_article_text(url)
                if article_text:
                    logger.info(f"Retrieved {len(article_text)} characters of article text")
                else:
                    logger.info("Failed to retrieve article text")
            
            # Classify and summarize
            logger.info("Classifying and summarizing with OpenAI")
            classification = classify_and_summarize(title, url or "", article_text)
            
            if not classification:
                logger.warning("Classification failed, skipping story")
                continue
            
            # Skip if not related
            if not classification.get("is_related", False):
                logger.info("Story not related to AI/ML, skipping")
                continue
            
            # Truncate text to safe length
            if article_text and len(article_text) > MAX_TEXT_LENGTH:
                article_text = article_text[:MAX_TEXT_LENGTH]
            
            # Save to database
            db = SessionLocal()
            try:
                story = Story(
                    hn_id=story_id,
                    title=title,
                    url=url,
                    text=article_text,
                    score=score,
                    by=item.get("by"),
                    time=item.get("time"),
                    category=classification.get("category"),
                    subcategory=classification.get("subcategory"),
                    summary=classification.get("summary"),
                    tags=classification.get("tags"),
                    relevance=classification.get("relevance"),
                    is_processed=True
                )
                db.add(story)
                db.commit()
                db.refresh(story)
                logger.info(f"✓ Saved story {story_id}: {title}")
                saved_count += 1
            except Exception as e:
                logger.error(f"Failed to save story {story_id}: {e}")
                db.rollback()
            finally:
                db.close()
            
            processed_count += 1
            
        except Exception as e:
            logger.error(f"Error processing story {story_id}: {e}")
            continue
    
    logger.info(f"Scraping complete. Processed: {processed_count}, Saved: {saved_count}")


if __name__ == "__main__":
    run_once()
