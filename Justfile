# Centavo - Just Commands
# Run `just` or `just --list` to see all available commands

# Show all available commands
default:
    @just --list

# Development Commands

# Start all services with Docker Compose
dev:
    docker compose -f docker/docker-compose.dev.yml up

# Start backend only
dev-backend:
    cd backend && uv run uvicorn app.main:app --reload --reload-dir app --host 0.0.0.0 --port 8000

# Start frontend only
dev-frontend:
    cd frontend && npm run dev

# Stop all Docker services
stop:
    docker compose -f docker/docker-compose.dev.yml down

# Kill backend server process
kill-backend:
    @echo "Killing backend processes..."
    @pkill -9 -f "uvicorn app.main:app" 2>/dev/null || true
    @pkill -9 -f "uvicorn" 2>/dev/null || true
    @pkill -9 -f "uv run uvicorn" 2>/dev/null || true
    @lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    @echo "✓ Backend processes killed"

# Kill all development processes
kill-all:
    @echo "Killing all development processes..."
    @pkill -9 -f "uvicorn" 2>/dev/null || true
    @pkill -9 -f "node" 2>/dev/null || true
    @lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    @lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    @echo "✓ All development processes killed"

# Database Commands

# Run database migrations
db-migrate:
    cd backend && uv run alembic upgrade head

# Rollback last migration
db-rollback:
    cd backend && uv run alembic downgrade -1

# Create a new migration
db-create-migration name:
    cd backend && uv run alembic revision --autogenerate -m "{{name}}"

# Seed default categories
db-seed:
    cd backend && PYTHONPATH=. uv run python ../scripts/seed_categories.py

# Testing Commands

# Run all tests
test: test-backend test-frontend

# Run backend tests
test-backend:
    cd backend && uv run pytest tests/ -v --cov=app

# Run frontend tests
test-frontend:
    cd frontend && npm run test

# Generate coverage report
test-coverage:
    cd backend && uv run pytest tests/ -v --cov=app --cov-report=html

# Code Quality Commands

# Run linters
lint:
    cd backend && uv run ruff check app/
    cd frontend && npm run lint

# Format code
format:
    cd backend && uv run ruff format app/
    cd frontend && npm run format

# Run type checking
typecheck:
    cd backend && uv run pyrefly check app/
    cd frontend && npm run type-check

# Production Commands

# Build Docker images
build:
    docker compose -f docker/docker-compose.yml build

# Deploy to production (placeholder)
deploy:
    @echo "Deploy command not yet implemented"

# Utility Commands

# Clean generated files
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    cd backend && rm -rf .venv dist build *.egg-info
    cd frontend && rm -rf .next out node_modules/.cache
