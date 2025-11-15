"""
OpenAI-powered story classification and summarization.
"""
import os
import json
import re
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def classify_and_summarize(title: str, url: Optional[str], text: Optional[str]) -> Dict:
    """
    Classify and summarize a story using OpenAI's API.
    
    Args:
        title: Story title
        url: Story URL (optional)
        text: Extracted article text (optional)
        
    Returns:
        Dictionary with keys:
            - is_related: bool indicating if story is relevant
            - category: string or None
            - subcategory: string or None
            - summary: string (2-3 sentences)
            - tags: string (comma-separated)
            - relevance: float (0-1)
    """
    # Build context for the prompt
    context = f"Title: {title}\n"
    if url:
        context += f"URL: {url}\n"
    if text:
        # Truncate text to avoid token limits
        context += f"Content: {text[:5000]}\n"
    
    prompt = f"""Analyze the following Hacker News story and determine if it's related to AI, machine learning, or related technologies.

{context}

Provide your analysis in strict JSON format with these exact keys:
- is_related: boolean (true if related to AI/ML/tech, false otherwise)
- category: string or null (e.g., "Machine Learning", "Artificial Intelligence", "Software Development", "Hardware", etc.)
- subcategory: string or null (e.g., "LLM", "Computer Vision", "DevOps", "Cloud", etc.)
- summary: string (2-3 sentence summary)
- tags: array of strings (relevant tags like ["gpt", "neural-networks", "python"])
- relevance: float between 0 and 1 (how relevant is this to AI/ML)

Return ONLY valid JSON, no additional text."""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a technical content analyst specializing in AI and technology topics. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=512
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON if wrapped in code blocks or extra text
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
        
        result = json.loads(content)
        
        # Normalize tags to comma-separated string
        if isinstance(result.get("tags"), list):
            result["tags"] = ",".join(result["tags"])
        
        # Ensure all required keys exist
        return {
            "is_related": result.get("is_related", False),
            "category": result.get("category"),
            "subcategory": result.get("subcategory"),
            "summary": result.get("summary", ""),
            "tags": result.get("tags", ""),
            "relevance": result.get("relevance", 0.0)
        }
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        print(f"Response content: {content}")
        return {
            "is_related": False,
            "category": None,
            "subcategory": None,
            "summary": "",
            "tags": "",
            "relevance": 0.0
        }
    except Exception as e:
        print(f"Error in classify_and_summarize: {e}")
        return {
            "is_related": False,
            "category": None,
            "subcategory": None,
            "summary": "",
            "tags": "",
            "relevance": 0.0
        }
