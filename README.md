# Centavo - Personal Expense Tracker

A personal expense/income tracker with Telegram Bot and Web Dashboard.

## Features

- 🤖 **Telegram Bot**: Natural language input for expenses/incomes
- 📊 **Web Dashboard**: Beautiful analytics and transaction management
- 💰 **Multi-currency**: Support for different currencies (MXN default)
- 📈 **Analytics**: Charts and reports by day/week/month/year
- 🌐 **Bilingual**: English and Spanish support

## Tech Stack

### Backend
- Python 3.14
- FastAPI 0.124.0
- SQLAlchemy 2.0.44 (async)
- Pydantic 2.12.5
- python-telegram-bot 22.5
- PostgreSQL 16
- Redis 7.x

### Frontend
- Next.js 16
- React 19.2
- Tailwind CSS 4.0
- TypeScript 5.x
- shadcn/ui

## Quick Start

### Prerequisites
- Python 3.14+
- Node.js 18+
- Docker & Docker Compose
- uv (Python package manager)

### Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/centavo.git
   cd centavo
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   # Edit the .env files with your configuration
   ```

3. **Start all services**
   ```bash
   just dev
   ```

   Or start services individually:
   ```bash
   just dev-backend  # Backend only
   just dev-frontend # Frontend only
   ```

4. **Run migrations**
   ```bash
   just db-migrate
   ```

5. **Access the application**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Frontend: http://localhost:3000

## Project Structure

```
centavo/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── docker/           # Docker configurations
├── docs/             # Documentation
├── scripts/          # Utility scripts
└── .github/          # CI/CD workflows
```

## Development Commands

```bash
just                 # Show all available commands
just dev             # Start all services
just test            # Run all tests
just lint            # Run linters
just format          # Format code
just db-migrate      # Run database migrations
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Gregory Onasis Gomez