# TaskAPI 🚀

A scalable REST API built with **FastAPI**, featuring JWT authentication, role-based access control, and full Task CRUD — with a React frontend.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Uvicorn |
| Database | PostgreSQL + SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Validation | Pydantic v2 |
| API Docs | Swagger UI (built-in) |
| Frontend | React (CDN) + Vanilla HTML/CSS |
| Deploy | Docker + Docker Compose |

---

## Project Structure

```
taskapi/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py       # Register, login, /me
│   │   │   ├── tasks.py      # CRUD for tasks
│   │   │   └── admin.py      # Admin user management
│   │   └── router.py         # Mounts all v1 routes
│   ├── core/
│   │   ├── config.py         # Settings via pydantic-settings
│   │   └── security.py       # JWT + bcrypt helpers
│   ├── db/
│   │   └── session.py        # SQLAlchemy engine + get_db
│   ├── models/
│   │   ├── user.py           # User ORM model
│   │   └── task.py           # Task ORM model
│   ├── schemas/
│   │   ├── user.py           # Pydantic request/response schemas
│   │   └── task.py           # Pydantic request/response schemas
│   ├── services/
│   │   └── auth_deps.py      # get_current_user, require_admin deps
│   └── main.py               # FastAPI app, CORS, exception handler
├── frontend/
│   └── index.html            # React SPA (single file, no build needed)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

---

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone and start everything (API + PostgreSQL)
git clone <https://github.com/sachinpeoplepro10/backend-assingment.git>
cd taskapi
docker-compose up --build
```

API: http://localhost:8000  
Swagger Docs: http://localhost:8000/docs  
Frontend: http://localhost:3000

---

### Option 2: Local Setup

**Prerequisites**: Python 3.11+, PostgreSQL running

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY

# 4. Start the server (tables auto-created on startup)
uvicorn app.main:app --reload
```

---

## API Endpoints

All routes are prefixed with `/api/v1`.

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | ❌ | Register new user |
| POST | `/auth/login` | ❌ | Login → JWT token |
| GET | `/auth/me` | ✅ | Get current user |

### Tasks
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/tasks/` | ✅ | List tasks (own; admin: all) |
| POST | `/tasks/` | ✅ | Create task |
| GET | `/tasks/{id}` | ✅ | Get task by ID |
| PATCH | `/tasks/{id}` | ✅ | Update task |
| DELETE | `/tasks/{id}` | ✅ | Delete task |

Query params for GET `/tasks/`: `status`, `priority`, `skip`, `limit`

### Admin
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/admin/users` | 🔐 Admin | List all users |
| PATCH | `/admin/users/{id}/deactivate` | 🔐 Admin | Deactivate user |
| PATCH | `/admin/users/{id}/activate` | 🔐 Admin | Activate user |
| DELETE | `/admin/users/{id}` | 🔐 Admin | Delete user |

---

## Authentication Flow

```
1. POST /api/v1/auth/register  →  Create account
2. POST /api/v1/auth/login     →  Get JWT token
3. Add header: Authorization: Bearer <token>
4. Access protected routes
```

JWT payload: `{ "sub": "<user_id>", "role": "user|admin", "exp": <timestamp> }`

---

## Role-Based Access

| Capability | User | Admin |
|-----------|------|-------|
| CRUD own tasks | ✅ | ✅ |
| View/edit all tasks | ❌ | ✅ |
| List all users | ❌ | ✅ |
| Activate/deactivate users | ❌ | ✅ |
| Delete users | ❌ | ✅ |

---

## Scalability Notes

### Current Architecture
- **Stateless JWT auth** — horizontally scalable; any server can verify tokens
- **SQLAlchemy connection pooling** — efficient DB connection reuse
- **Pydantic v2 validation** — fast, compiled validators

### Scaling to Production

**1. Caching (Redis)**
```python
# Cache task lists per user to reduce DB load
@router.get("/tasks/")
async def list_tasks(...):
    cache_key = f"tasks:user:{current_user.id}:{status}"
    cached = await redis.get(cache_key)
    if cached: return json.loads(cached)
    # ... fetch from DB, store in Redis with TTL
```

**2. Async Database**
Switch to `asyncpg` + `SQLAlchemy async` for non-blocking DB calls under high concurrency.

**3. Microservices Split**
```
api-gateway        (rate limiting, auth routing)
auth-service       (register, login, token verify)
task-service       (CRUD, owned by domain)
notification-svc   (email, webhook on task update)
```

**4. Load Balancing**
Deploy multiple Uvicorn workers behind Nginx or a cloud load balancer:
```bash
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

**5. Database**
- Read replicas for heavy GET workloads
- Partition `tasks` table by `owner_id` at scale
- Add indices on `owner_id`, `status`, `created_at`

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | required |
| `SECRET_KEY` | JWT signing key (min 32 chars) | required |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `30` |

---

## API Documentation

Interactive Swagger UI is auto-generated at:  
👉 **http://localhost:8000/docs**

To authenticate in Swagger:
1. Use `POST /api/v1/auth/login` to get a token
2. Click the 🔒 **Authorize** button (top right)
3. Enter: `<your_token>` (without "Bearer")
4. All subsequent requests will include the auth header
