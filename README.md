# HN AI Scraper

A production-ready scraper that fetches Hacker News stories, classifies and summarizes them using OpenAI's ChatGPT API, and stores relevant AI/ML-related stories in a PostgreSQL database.

## Features

- **Automated HN Scraping**: Fetches top stories from Hacker News using the Firebase API
- **Intelligent Filtering**: Pre-filters stories by keywords and score thresholds
- **Content Extraction**: Extracts full article text using newspaper3k with BeautifulSoup fallback
- **AI-Powered Classification**: Uses OpenAI ChatGPT to classify, summarize, and tag stories
- **PostgreSQL Storage**: Stores relevant stories with metadata in PostgreSQL (SQLite supported for development)
- **FastAPI REST API**: Query stored stories via a RESTful API
- **Configurable**: Fully configurable via environment variables

## Project Structure

```
hn-ai-scraper/
├── hn_scraper/
│   ├── models.py       # SQLAlchemy data models
│   ├── db.py           # Database connection and initialization
│   ├── hn_client.py    # Hacker News API client
│   ├── fetcher.py      # Article content extraction
│   ├── processor.py    # OpenAI classification and summarization
│   └── scraper.py      # Main orchestrator script
├── app/
│   └── main.py         # FastAPI application
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
└── README.md           # This file
```

## Prerequisites

- Python 3.8+
- PostgreSQL database (or SQLite for local development)
- OpenAI API key

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/arunb2/hn-ai-scraper.git
   cd hn-ai-scraper
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL or SQLite connection string | `postgresql://user:pass@localhost:5432/hn_ai_scraper` |
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-3.5-turbo` or `gpt-4` |
| `HN_MAX_STORIES` | Maximum number of top stories to fetch | `100` |
| `KEYWORDS` | Comma-separated keywords for pre-filtering | `AI,ML,machine learning,LLM` |
| `SCRAPE_MIN_SCORE` | Minimum HN score to process | `10` |
| `PORT` | Port for the FastAPI server | `8000` |

## Database Setup

### PostgreSQL (Production)

1. **Create a PostgreSQL database**:
   ```sql
   CREATE DATABASE hn_ai_scraper;
   ```

2. **Update DATABASE_URL in .env**:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/hn_ai_scraper
   ```

3. **Initialize the database** (tables are created automatically on first run):
   ```bash
   python -c "from hn_scraper.db import init_db; init_db()"
   ```

### SQLite (Local Development)

For local development, you can use SQLite:
```
DATABASE_URL=sqlite:///./hn_ai_scraper.db
```

The database file will be created automatically on first run.

## Running Locally

### Run the Scraper

To scrape and process stories once:

```bash
python -m hn_scraper.scraper
```

This will:
1. Fetch top stories from Hacker News
2. Filter by keywords and minimum score
3. Extract article content
4. Classify and summarize with OpenAI
5. Store relevant stories in the database

### Run the API Server

To start the FastAPI server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or use the PORT environment variable:

```bash
PORT=8000 uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Access the API at:
- **Root**: http://localhost:8000/
- **Interactive docs**: http://localhost:8000/docs
- **List stories**: http://localhost:8000/stories
- **Search stories**: http://localhost:8000/stories?q=GPT&limit=10
- **Get story**: http://localhost:8000/stories/{hn_id}

## Running on a Server

### Setup

1. **Clone and install** as described above
2. **Configure environment variables** in `.env`
3. **Set up PostgreSQL** database
4. **Install as a system service** (optional)

### Scheduling the Scraper

Use cron to run the scraper periodically:

```bash
# Edit crontab
crontab -e

# Add entry to run every hour
0 * * * * cd /path/to/hn-ai-scraper && /path/to/venv/bin/python -m hn_scraper.scraper >> /var/log/hn-scraper.log 2>&1
```

### Running the API Server

For production deployment, use a process manager like systemd or supervisor:

**Example systemd service** (`/etc/systemd/system/hn-scraper-api.service`):

```ini
[Unit]
Description=HN AI Scraper API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/hn-ai-scraper
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable hn-scraper-api
sudo systemctl start hn-scraper-api
```

## OpenAI API Usage

- The scraper uses OpenAI's Chat API to classify and summarize stories
- **Cost**: Each story processed costs approximately 1-2 cents (depending on model and content length)
- **Model**: Configurable via `OPENAI_MODEL` (default: `gpt-3.5-turbo`)
- **Rate limits**: Be mindful of OpenAI's rate limits when processing large batches
- The prompt is designed to return structured JSON with low temperature (0.0) for consistency

### Cost Estimation

For `gpt-3.5-turbo`:
- ~100 stories/hour = ~$1-2/hour
- ~2,400 stories/day = ~$24-48/day

Consider implementing rate limiting or batch processing for cost control.

## PostgreSQL Notes

- The application creates tables automatically using SQLAlchemy
- For production, consider using Alembic for migrations (not included in this version)
- The `Story` model includes indexes on `hn_id` and `id` for fast lookups
- The `text` field is stored as TEXT type, supporting long article content (truncated to 20,000 characters)

## API Endpoints

### GET /stories

List stories with optional search and pagination.

**Query Parameters**:
- `q` (optional): Search term for title, summary, or tags
- `limit` (optional, default: 50): Maximum number of stories to return (1-500)

**Example**:
```bash
curl "http://localhost:8000/stories?q=GPT&limit=10"
```

### GET /stories/{hn_id}

Get a specific story by its Hacker News ID.

**Example**:
```bash
curl "http://localhost:8000/stories/38765432"
```

## Troubleshooting

### Database Connection Issues

- **PostgreSQL**: Ensure the database exists and credentials are correct
- **SQLite**: Check file permissions and path in `DATABASE_URL`

### OpenAI API Issues

- Verify `OPENAI_API_KEY` is set correctly
- Check API rate limits and quota
- Review logs for API error messages

### Article Fetching Issues

- Some sites block scrapers; the fetcher includes a user-agent header
- newspaper3k may fail on some sites; BeautifulSoup is used as fallback
- Paywalled content cannot be extracted

## Next Steps & Future Improvements

- **Prompt Tuning**: Refine the classification prompt for better accuracy
- **Rate Limiting**: Implement request throttling for OpenAI API cost control
- **Batch Processing**: Add support for bulk processing with delays
- **Alembic Migrations**: Set up database migrations for schema changes
- **Tag Normalization**: Create a separate tags table with many-to-many relationship
- **Caching**: Add caching layer for API responses
- **Monitoring**: Implement health checks and metrics
- **Testing**: Add unit and integration tests

## License

MIT License - see LICENSE file for details
