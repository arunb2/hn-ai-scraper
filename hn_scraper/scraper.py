"""
Main scraper orchestrator that fetches, processes, and stores HN stories.
"""
import os
from dotenv import load_dotenv
from .db import init_db, SessionLocal
from .models import Story
from .hn_client import fetch_top_story_ids, fetch_item
from .fetcher import fetch_article_text
from .processor import classify_and_summarize

load_dotenv()

HN_MAX_STORIES = int(os.getenv("HN_MAX_STORIES", "100"))
KEYWORDS = [k.strip().lower() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]
SCRAPE_MIN_SCORE = int(os.getenv("SCRAPE_MIN_SCORE", "10"))


def matches_keywords(title: str, url: str) -> bool:
    """Check if title or URL matches any of the configured keywords."""
    if not KEYWORDS:
        return True
    
    search_text = f"{title} {url}".lower()
    return any(keyword in search_text for keyword in KEYWORDS)


def run_once(limit: Optional[int] = None):
    """
    Run the scraper once to fetch and process top HN stories.
    
    Args:
        limit: Maximum number of stories to process (defaults to HN_MAX_STORIES)
    """
    if limit is None:
        limit = HN_MAX_STORIES
    
    print(f"Starting HN scraper (limit={limit}, min_score={SCRAPE_MIN_SCORE})")
    
    # Initialize database
    init_db()
    
    # Fetch top story IDs
    print("Fetching top story IDs...")
    story_ids = fetch_top_story_ids(limit)
    print(f"Found {len(story_ids)} story IDs")
    
    session = SessionLocal()
    processed_count = 0
    saved_count = 0
    
    try:
        for idx, story_id in enumerate(story_ids, 1):
            print(f"\n[{idx}/{len(story_ids)}] Processing story {story_id}...")
            
            try:
                # Fetch story data
                item = fetch_item(story_id)
                if not item:
                    print(f"  Skipping: Item {story_id} not found")
                    continue
                
                # Only process stories (not jobs, polls, etc.)
                if item.get("type") != "story":
                    print(f"  Skipping: Not a story (type={item.get('type')})")
                    continue
                
                # Check minimum score
                score = item.get("score", 0)
                if score < SCRAPE_MIN_SCORE:
                    print(f"  Skipping: Score {score} below threshold {SCRAPE_MIN_SCORE}")
                    continue
                
                # Check if already in database
                existing = session.query(Story).filter_by(hn_id=story_id).first()
                if existing:
                    print(f"  Skipping: Story {story_id} already in database")
                    continue
                
                title = item.get("title", "")
                url = item.get("url", "")
                
                # Pre-filter by keywords (if score < 50)
                if score < 50 and not matches_keywords(title, url):
                    print(f"  Skipping: No keyword match and score {score} < 50")
                    continue
                
                # Fetch article text if URL exists
                article_text = None
                if url:
                    print(f"  Fetching article text from {url[:60]}...")
                    article_text = fetch_article_text(url)
                    if article_text:
                        print(f"  Fetched {len(article_text)} characters")
                    else:
                        print("  Failed to fetch article text")
                
                # Classify and summarize
                print("  Classifying with OpenAI...")
                classification = classify_and_summarize(title, url, article_text)
                
                # Skip if not related
                if not classification["is_related"]:
                    print(f"  Skipping: Not relevant (relevance={classification['relevance']})")
                    continue
                
                # Truncate text to avoid database issues
                if article_text and len(article_text) > 20000:
                    article_text = article_text[:20000]
                
                # Create and save story
                story = Story(
                    hn_id=story_id,
                    title=title,
                    url=url,
                    text=article_text,
                    score=score,
                    by=item.get("by"),
                    time=item.get("time"),
                    category=classification["category"],
                    subcategory=classification["subcategory"],
                    summary=classification["summary"],
                    tags=classification["tags"],
                    relevance=classification["relevance"],
                    is_processed=True
                )
                
                session.add(story)
                session.commit()
                saved_count += 1
                
                print(f"  ✓ Saved: {title[:60]}... (relevance={classification['relevance']:.2f})")
                
            except Exception as e:
                print(f"  Error processing story {story_id}: {e}")
                session.rollback()
                continue
            
            processed_count += 1
    
    finally:
        session.close()
    
    print(f"\n{'='*60}")
    print(f"Scraper completed: Processed {processed_count}, Saved {saved_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    from typing import Optional
    run_once()
