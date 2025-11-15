# HN AI Scraper

A production-ready scraper that fetches Hacker News stories, classifies and summarizes them using OpenAI's ChatGPT API, and stores relevant stories in a Postgres database.

## Features

- **Intelligent Filtering**: Uses OpenAI to classify stories by relevance, category, and tags
- **Automated Summarization**: Generates concise 2-3 sentence summaries of articles
- **PostgreSQL Storage**: Stores processed stories with metadata and classification results
- **REST API**: FastAPI-based API to query and retrieve stored stories
- **Configurable**: Environment-based configuration for easy deployment
- **Keyword Pre-filtering**: Reduces API costs by pre-filtering stories by keywords and score
- **Robust Article Fetching**: Uses newspaper3k with BeautifulSoup fallback for content extraction

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database Configuration (Postgres recommended for production)
DATABASE_URL=postgresql://username:password@localhost:5432/hn_scraper

# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Scraper Configuration
HN_MAX_STORIES=100
KEYWORDS=ai,ml,machine learning,artificial intelligence,gpt,llm,neural
SCRAPE_MIN_SCORE=10

# API Configuration
PORT=8000
```

### Environment Variables Explained:

- **DATABASE_URL**: PostgreSQL connection string. Format: `postgresql://user:pass@host:port/dbname`
- **OPENAI_API_KEY**: Your OpenAI API key (required for classification/summarization)
- **OPENAI_MODEL**: OpenAI model to use (default: `gpt-4o-mini` for cost efficiency)
- **HN_MAX_STORIES**: Maximum number of top stories to process per run
- **KEYWORDS**: Comma-separated keywords for pre-filtering (case-insensitive)
- **SCRAPE_MIN_SCORE**: Minimum HN score threshold for processing stories
- **PORT**: Port for the FastAPI server

## Quickstart

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/arunb2/hn-ai-scraper.git
   cd hn-ai-scraper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your DATABASE_URL and OPENAI_API_KEY
   ```

4. **Run the scraper**:
   ```bash
   python -m hn_scraper.scraper
   ```

5. **Start the API server**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

6. **Access the API**:
   - View all stories: `http://localhost:8000/stories`
   - Search stories: `http://localhost:8000/stories?q=machine+learning&limit=10`
   - Get specific story: `http://localhost:8000/stories/{hn_id}`

### Server Deployment

1. **Set up PostgreSQL database**:
   ```bash
   # Create database
   createdb hn_scraper
   ```

2. **Configure environment variables** on your server (via systemd, supervisor, or container orchestration)

3. **Run database initialization**:
   ```bash
   python -c "from hn_scraper.db import init_db; init_db()"
   ```

4. **Schedule periodic scraping** (e.g., via cron):
   ```bash
   # Run every hour
   0 * * * * cd /path/to/hn-ai-scraper && /path/to/python -m hn_scraper.scraper
   ```

5. **Deploy API server** (e.g., via systemd, supervisor, or container):
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

## OpenAI API Key

You'll need an OpenAI API key to use this scraper. Get one at: https://platform.openai.com/api-keys

**Note**: Each story classification/summarization uses tokens. The scraper uses `gpt-4o-mini` by default for cost efficiency. Monitor your usage at: https://platform.openai.com/usage

**Cost Control Tips**:
- Use keyword pre-filtering (KEYWORDS env var) to reduce API calls
- Set appropriate SCRAPE_MIN_SCORE to filter low-quality stories
- Use HN_MAX_STORIES to limit processing per run
- Consider caching results to avoid reprocessing

## Running the Scraper

The scraper can be run on-demand or scheduled:

```bash
# Run once
python -m hn_scraper.scraper

# Or schedule with cron (example: every hour)
0 * * * * cd /path/to/hn-ai-scraper && /usr/bin/python3 -m hn_scraper.scraper >> /var/log/hn-scraper.log 2>&1
```

## Running the API

Start the FastAPI server:

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Access the interactive API docs at `http://localhost:8000/docs`

## API Endpoints

- `GET /stories` - List all stories (supports `q` for search and `limit` for pagination)
- `GET /stories/{hn_id}` - Get a specific story by Hacker News ID

## Recommended Next Steps

1. **Prompt Tuning**: Refine the classification prompt in `processor.py` to better match your needs
2. **Rate Limiting & Cost Control**: Implement rate limiting for OpenAI API calls and set daily cost budgets
3. **Database Migrations**: Use Alembic for proper schema migrations as the project evolves
4. **Tag Normalization**: Normalize tags into a separate table for better querying and analytics
5. **Monitoring**: Add logging, metrics, and alerting for production deployment
6. **Caching**: Implement caching to avoid reprocessing stories
7. **Background Processing**: Move scraping to background jobs (e.g., Celery, RQ)
8. **Testing**: Add unit and integration tests for reliability

## License

See LICENSE file for details.
