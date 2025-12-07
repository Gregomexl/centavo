# Centavo Backend

Personal expense tracker backend API built with FastAPI, SQLAlchemy, and PostgreSQL.

## Tech Stack

- Python 3.14
- FastAPI 0.124.0
- SQLAlchemy 2.0.44 (async)
- Pydantic 2.12.5
- PostgreSQL 16
- Redis 7.x

## Development

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn centavo.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```
