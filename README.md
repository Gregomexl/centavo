# Centavo 🪙

A personal finance tracker built for self-hosting. Track expenses, manage categories, and visualize your financial health with a modern dashboard and Telegram bot integration.

## Features
- 📊 **Dashboard**: Real-time overview of expenses, income, and balance.
- 💸 **Transaction Tracking**: Easy entry for expenses and income.
- 🏷️ **Categories**: Custom categories with emoji support.
- 🤖 **Telegram Bot**: Log expenses on-the-go via chat.
- 🔒 **Self-Hosted**: Privacy-first, runs on your own hardware (Mac Mini, VPS, Raspberry Pi).
- ☁️ **Cloudflare Tunnel**: Secure external access without port forwarding.

## 📚 Documentation
- **[User Guide](docs/USER_GUIDE.md)**: How to use the dashboard and Telegram bot.
- **[Deployment Guide](docs/MAC_MINI_DEPLOYMENT.md)**: Detailed self-hosting instructions.

## Tech Stack
- **Frontend**: Next.js 16 (App Router), Tailwind CSS 4, Recharts
- **Backend**: FastAPI (Python 3.12), SQLAlchemy, Alembic
- **Database**: PostgreSQL
- **Infrastructure**: Docker Compose, Cloudflare Tunnel

---

## 🚀 Getting Started

### Prerequisites
- [Docker & Docker Compose](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/downloads)
- A domain name (optional but recommended for external access)
- A Cloudflare account (free)

### 1. Clone the Repository
```bash
git clone https://github.com/Gregomexl/centavo.git
cd centavo
```

### 2. Environment Setup
Create the production environment variables:

**Backend**:
```bash
cp backend/.env.example backend/.env.production
# Edit backend/.env.production and set your secrets (DB password, Telegram Token, etc.)
```

**Frontend**:
```bash
# Create .env.production for the frontend
echo "NEXT_PUBLIC_API_URL=https://api.yourdomain.com" > frontend/.env.production
```

### 3. Deploy (Production)
Run the application using the production compose file. This includes the database, redis, backend, frontend, bot, and the secure tunnel.

**Important**: You need a `TUNNEL_TOKEN` from Cloudflare Zero Trust.
1. Go to Cloudflare Zero Trust > Networks > Tunnels.
2. Create a tunnel and copy the token.
3. Edit `docker-compose.prod.yml` and paste your token in the `tunnel` service.
4. Configure routes in Cloudflare:
   - `app.yourdomain.com` -> `http://frontend:3000`
   - `api.yourdomain.com` -> `http://backend:8000`

**Start the stack:**
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Access your dashboard at `https://app.yourdomain.com`!

### 4. Development
To run locally for development:
```bash
docker compose -f docker/docker-compose.dev.yml up -d
```
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs