# VicAI FastAPI Backend (Identity & Tenant Foundation)

Welcome to the **VicAI API**. This project currently serves as the multi-tenant identity and access management foundation for the VicAI platform.

## Current Features (Implemented)

- **Multi-Tenant Identity Foundation:** Customers are automatically assigned a `Tenant` (Organization) upon registration, establishing logical boundaries for their data.
- **Role-Based Access Control (RBAC):** Foundation for organization-based membership. Users have specific roles (e.g., `owner`) and platform designations (`admin` vs. `customer`).
- **Authentication System:** 
  - Separate login flows for administrators (using environment-based credentials) and customers.
  - Customer passwords are securely hashed using Argon2 (`pwdlib`).
  - Protected API routes via short-lived, signed JWT Bearer tokens.
- **Invitation System:** APIs for creating and managing invitations for new members to join existing tenants.
- **Internal Admin Endpoints:** Administrative controls for managing the platform.

## Technology Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Database:** PostgreSQL (optimized for Supabase)
- **ORM & Migrations:** SQLAlchemy 2.0 & Alembic
- **Package Management:** [uv](https://github.com/astral-sh/uv)
- **Authentication:** JWT (JSON Web Tokens) & Argon2 (`pwdlib`)

---

## Getting Started (Local Development)

### 1. Environment Setup

Copy the example environment file and configure your local settings. You will need a strong admin password and JWT secret:

```bash
cp .env.example .env
openssl rand -hex 32
```

> **Note on Database Connection:**
> If you are connecting to a Supabase database and your local machine does not support IPv6, set `SUPABASE_POOLER_HOST` in your `.env` to the session-pooler host found in your Supabase dashboard (**Connect → Session pooler**). Leave the pooler on port `5432`; the application will adapt the direct URL automatically.

### 2. Install Dependencies & Migrate Database

We use `uv` for dependency management.

```bash
# Install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head
```

### 3. Run the Development Server

Start the API with hot-reloading enabled:

```bash
uv run uvicorn app.main:app --reload
```

- **API Documentation:** Interactive Swagger UI is available at `http://127.0.0.1:8000/docs`.
- **Health Check:** `GET http://127.0.0.1:8000/health`

---

## Authentication Endpoints

The API uses JWT bearer tokens for protected routes.

### Register a Customer (Auto-creates Tenant)

```bash
curl -X POST http://127.0.0.1:8000/api/auth/registration \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "customer@example.com",
    "password": "a-strong-customer-password",
    "full_name": "Example Customer",
    "platform": "customer",
    "role": "owner"
  }'
```

### Log In as a Customer

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "customer@example.com",
    "password": "a-strong-customer-password"
  }'
```

### Log In as the Administrator

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "vicai_admin",
    "password": "the-value-from-your-env"
  }'
```

### Access Protected Routes (e.g., Profile)

Attach the returned access token as a Bearer token in the `Authorization` header:

```bash
curl http://127.0.0.1:8000/api/auth/profile \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

---

## Internal Admin Endpoints

Requires a valid token with the `admin` platform role.

### List All Users

```bash
curl -X GET http://127.0.0.1:8000/api/internal-admin/users \
  -H 'Authorization: Bearer YOUR_ADMIN_TOKEN'
```

### List All Organizations (Tenants)

```bash
curl -X GET http://127.0.0.1:8000/api/internal-admin/organizations \
  -H 'Authorization: Bearer YOUR_ADMIN_TOKEN'
```

---

## Invitation Endpoints

Requires an organization admin token to send invitations.

### Send an Invitation

```bash
curl -X POST http://127.0.0.1:8000/api/invitations \
  -H 'Authorization: Bearer YOUR_CUSTOMER_OWNER_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "new_team_member@example.com"
  }'
```

### Accept an Invitation

```bash
curl -X POST http://127.0.0.1:8000/api/invitations/accept \
  -H 'Content-Type: application/json' \
  -d '{
    "token": "INVITATION_TOKEN_FROM_EMAIL",
    "password": "new-user-password",
    "full_name": "New Team Member"
  }'
```

---

## Testing & Quality Assurance

The test suite runs against an isolated, in-memory SQLite database, ensuring your configured Postgres database is never modified during tests.

```bash
# Run tests
uv run pytest

# Run linter
uv run ruff check .
```
