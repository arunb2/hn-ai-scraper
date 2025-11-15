"""OpenAI processor for classifying and summarizing HN stories."""
import os
import json
import logging
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

CLASSIFICATION_PROMPT = """You are an AI assistant that classifies and summarizes Hacker News stories related to AI, ML, and related technologies.

Analyze the following story and return a JSON object with these exact keys:
- is_related: boolean (true if related to AI/ML/tech, false otherwise)
- category: string or null (main category like "Machine Learning", "AI Research", "Tools", etc.)
- subcategory: string or null (more specific subcategory)
- summary: string (2-3 sentence summary of the story)
- tags: array of strings (relevant tags like ["NLP", "GPT", "Computer Vision"])
- relevance: float between 0 and 1 (how relevant is this to AI/ML)

Title: {title}
URL: {url}
Content: {text}

Return only valid JSON, no additional text."""


def classify_and_summarize(title: str, url: str, text: Optional[str]) -> Optional[Dict]:
    """
    Classify and summarize a story using OpenAI API.
    
    Args:
        title: Story title
        url: Story URL
        text: Article text (can be None)
        
    Returns:
        Dictionary with classification results or None if API call fails
    """
    if not client:
        logger.error("OpenAI client not initialized. Check OPENAI_API_KEY.")
        return None
    
    # Truncate text to reasonable length for API
    content_text = text[:3000] if text else "No content available"
    
    prompt = CLASSIFICATION_PROMPT.format(
        title=title,
        url=url or "No URL",
        text=content_text
    )
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=512
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON if model added extra text
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        result = json.loads(result_text)
        
        # Normalize tags to comma-separated string
        if "tags" in result and isinstance(result["tags"], list):
            result["tags"] = ",".join(result["tags"])
        
        # Validate required keys
        required_keys = ["is_related", "category", "subcategory", "summary", "tags", "relevance"]
        if not all(key in result for key in required_keys):
            logger.error(f"Missing required keys in API response: {result}")
            return None
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from OpenAI response: {e}")
        logger.debug(f"Response text: {result_text}")
        return None
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return None
