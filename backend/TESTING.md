# API Testing Guide

## Prerequisites

1. **Database running:**
   ```bash
   docker compose -f docker/docker-compose.dev.yml up -d postgres redis
   ```

2. **Environment configured:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and set SECRET_KEY and JWT_SECRET_KEY
   ```

3. **Migrations run:**
   ```bash
   cd backend
   PYTHONPATH=. uv run alembic upgrade head
   ```

4. **Seed categories (optional but recommended):**
   ```bash
   cd backend
   PYTHONPATH=. uv run python ../scripts/seed_categories.py
   ```

## Running Tests

### Option 1: Start server and run test script

**Terminal 1 - Start server:**
```bash
cd backend
PYTHONPATH=. uv run uvicorn app.main:app --reload
```

**Terminal 2 - Run tests:**
```bash
cd backend
uv run python test_api.py
```

### Option 2: Interactive API testing

Visit Swagger UI at: **http://localhost:8000/docs**

1. Register a user via `/api/v1/auth/register`
2. Login via `/api/v1/auth/login` and copy the `access_token`
3. Click "Authorize" button and paste: `Bearer YOUR_ACCESS_TOKEN`
4. Try all endpoints!

### Option 3: Manual curl commands

```bash
# Health check
curl http://localhost:8000/health

# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456","display_name":"Test User"}'

# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456"}' \
  | jq -r '.access_token')

# List categories
curl http://localhost:8000/api/v1/categories \
  -H "Authorization: Bearer $TOKEN"

# Create transaction
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type":"expense",
    "amount":50.99,
    "currency":"MXN",
    "description":"Lunch"
  }'

# List transactions
curl "http://localhost:8000/api/v1/transactions?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

## Expected Results

✅ All authentication endpoints work
✅ Can create, read, update, delete transactions  
✅ Can manage categories (system + custom)
✅ Pagination and filtering work
✅ Proper error handling and validation
