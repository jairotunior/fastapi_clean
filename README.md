# FastAPI Clean

A FastAPI application built with a clean architecture: domain, application, and infrastructure layers. It provides a REST API with authentication (JWT and OIDC/Keycloak), orders management, and PostgreSQL persistence.

## Features

- **FastAPI** with Pydantic v2 and async support
- **Clean architecture**: domain, application, and infrastructure separation
- **Database**: SQLAlchemy 2.0 + asyncpg, with Alembic migrations
- **Auth**: JWT (HS256) and optional OIDC/Keycloak (RS256 via JWKS)
- **Docker** support and **GitHub Actions** for test, lint, and container build/push

## Prerequisites

- Python 3.14+ (or 3.12+)
- PostgreSQL (for local development and migrations)
- Optional: Keycloak or another OIDC provider for OIDC auth

## Installation

1. Clone the repository and enter the project directory:

   ```bash
   cd fastapi_clean
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # Linux/macOS
   pip install -r requirements.txt
   pip install "psycopg[binary]"   # for local DB if not using asyncpg alone
   ```

3. Copy environment variables and adjust as needed:

   ```bash
   cp .env.example .env
   ```

   Or create a `.env` file with at least:

   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/your_db
   JWT_SECRET_KEY=your-secret-key
   JWT_ALGORITHM=HS256
   ```

   Optional for OIDC:

   ```env
   OIDC_JWKS_URL=http://localhost:9000/realms/your-realm/protocol/openid-connect/certs
   OIDC_ISSUER=http://localhost:9000/realms/your-realm
   OIDC_AUDIENCE=account
   ```

4. Run database migrations (Alembic):

   ```bash
   alembic -c infrastructure/driven/db/sqlalchemy/alembic.ini upgrade head
   ```

## Running locally

Start the API with Uvicorn:

```bash
uvicorn fastapi_clean.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Interactive docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

## Running with Docker

Build and run:

```bash
docker build -t fastapi_clean .
docker run -p 8000:8000 --env-file .env fastapi_clean
```

Or use Docker Compose if you add a `docker-compose.yml` that includes the app and PostgreSQL.

## Tests

Run tests (set `DATABASE_URL` if tests hit the database):

```bash
# Optional: use a test DB
set DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/test_db

pytest tests
```

Lint with Ruff:

```bash
ruff check .
```

## API overview

| Endpoint        | Description                    |
|----------------|--------------------------------|
| `GET /`        | Root message                   |
| `GET /health`  | Health check (excluded from OpenAPI) |
| `GET /items/`  | List items (query: `skip`, `limit`) |
| `POST /items/` | Create item (body: `OrderItem`) |
| `GET /items/{item_id}` | Get item by ID (optional query `q`, `short`) |
| `PUT /items/{item_id}` | Update item |
| `GET /users/{user_id}/items/{item_id}` | User item by IDs |
| `GET/POST /api/v1/...` | Auth and orders under API v1 prefix |

Authentication and orders are under the `/api/v1` prefix; see the OpenAPI schema at `/docs` for request/response shapes.

## Project structure

```
fastapi_clean/
├── core/                 # App config (e.g. settings)
├── domain/               # Domain entities and value objects
├── application/          # Use cases and ports
├── infrastructure/
│   ├── driving/         # HTTP API (FastAPI routes, schemas, deps)
│   └── driven/          # DB (SQLAlchemy, Alembic), auth (JWT/OIDC)
├── tests/
├── main.py              # FastAPI app entry
├── requirements.txt
├── Dockerfile
└── .github/workflows/   # CI: lint, test, build and push image to GHCR
```

## CI/CD

The `.github/workflows/test_and_build.yaml` workflow on push to `main`:

1. Sets up Python 3.14 and a PostgreSQL 16 service
2. Installs dependencies and runs **Ruff** lint
3. Runs **pytest** with `DATABASE_URL` pointing at the service
4. Builds the Docker image and pushes it to GitHub Container Registry (`ghcr.io`)

## License

MIT
