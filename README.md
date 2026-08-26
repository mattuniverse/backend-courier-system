# CourierPro — Backend API

FastAPI + asyncpg + PostgreSQL backend for the Courier & Parcel Management System.

## Setup

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and a strong SECRET_KEY

pip install -r requirements.txt

# Run the DB schema:
psql -U postgres -d courier_system -f schema.sql

uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Demo Credentials

| Role     | Username | Password  |
|----------|----------|-----------|
| Admin    | admin    | admin123  |
| Cashier  | cashier  | cashier123|

Generate your own bcrypt hashes for production:
```bash
python -c "from passlib.context import CryptContext; ctx=CryptContext(schemes=['bcrypt']); print(ctx.hash('YOUR-PASSWORD'))"
```

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (asyncpg)
- **Auth**: JWT (python-jose) + bcrypt
- **Rate Limiting**: slowapi

## Structure

```
backend/
├── routers/          # API route handlers
│   ├── auth.py       # Login / logout
│   ├── dashboard.py  # Stats & recent parcels
│   ├── users.py      # Admin user management
│   ├── customers.py  # Customer CRUD
│   ├── couriers.py   # Courier CRUD
│   ├── branches.py   # Branch CRUD
│   ├── parcels.py    # Parcel booking & status
│   └── tracking.py   # Public tracking endpoint
├── services/         # Business logic services
├── utils/
│   ├── auth.py       # JWT, password hashing, dependencies
│   └── tracking.py   # Tracking number generation
├── database.py       # asyncpg connection pool
├── models.py         # Enums
├── schemas.py        # Pydantic models
├── main.py           # FastAPI app
└── schema.sql        # PostgreSQL schema + seed data
```
