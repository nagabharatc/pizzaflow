# PizzaFlow AI

A full-stack restaurant management system built as a deliberate exercise in software architecture methodology — Domain-Driven Design, Clean Architecture, and bounded contexts applied to a real product problem.

> **Built for a pizza restaurant owner (Rajan) who needs to manage orders, track business intelligence, and ask natural-language questions about his business.**

---

## What it does

**Customer Portal** (public)
- Build and submit pizza orders — choose base, toppings, quantity
- Complete checkout with payment method (Card, Cash, UPI)
- Receive a fully itemised receipt with GST breakdown

**Admin Portal** (JWT-protected)
- Real-time analytics dashboard — revenue, sales, customer retention, payment distribution
- AI Restaurant Advisor — ask natural-language questions, get data-grounded answers
- Month-over-month and week-over-week growth metrics

---

## Architecture

The backend is organised into **6 bounded contexts**, each owning its own models, repository, service, and routes. No context reaches into another's internals.

```
Reference       →  Menu items (seed data, read-only)
Order           →  Customer + Order lifecycle (Pending state)
Checkout        →  Bill + Payment, atomic transition to Paid state
Analytics       →  Business Intelligence computed on every request (never persisted)
AI Advisor      →  Receives only the BI Model; LLM reasons, never calculates
Auth            →  JWT login; Customer Portal is public, Admin Portal is protected
```

**Key architectural principle:** Business Intelligence is computed by Python. The LLM only receives structured metrics and returns reasoning. It never touches the database, performs calculations, or sees raw data.

```
Request → AnalyticsService → Python computes BI Model
                                        ↓
                             AIService formats as text
                                        ↓
                             OpenRouterClient → GPT-4o-mini
                                        ↓
                             Natural language answer returned
```

Full architectural documentation lives in [`docs/`](docs/):

| Document | Contents |
|---|---|
| [System Architecture](docs/system_architecture.md) | Layers, components, data flow |
| [Bounded Contexts](docs/bounded_contexts.md) | Context map and ownership boundaries |
| [Architecture Principles](docs/architecture_principles.md) | 19 design principles with rationale |
| [Domain Model](docs/domain_model.md) | Entities, value objects, aggregates |
| [Database Design](docs/database_design.md) | Schema, relationships, constraints |
| [API Design](docs/api_design.md) | All endpoints, request/response shapes |
| [Business Rules](docs/business_rules.md) | Invariants enforced in domain layer |

---

## Tech stack

**Backend**
- Python 3.12 · FastAPI · SQLAlchemy (sync ORM) · Pydantic v2 · pydantic-settings
- SQLite (local/dev) · PostgreSQL (production-ready)
- python-jose (JWT) · httpx (OpenRouter HTTP client)
- pytest (118 tests, 0 failures)

**Frontend**
- React 18 · TypeScript · Vite
- Tailwind CSS · shadcn/ui primitives
- TanStack Query (server state) · React Hook Form + Zod (validation)
- Recharts (AreaChart, PieChart, BarChart) · Axios · React Router v6

**AI**
- OpenRouter API (OpenAI-compatible endpoint)
- Model: `openai/gpt-4o-mini`
- Provider-agnostic via `LLMClient` Protocol — swap models with one config change

---

## Folder structure

```
RESTURANT_MANAGEMENT/
├── backend/
│   ├── app/
│   │   ├── contexts/
│   │   │   ├── reference/       # Menu seed data
│   │   │   ├── order/           # Customer + Order entities
│   │   │   ├── checkout/        # Bill + Payment, atomic commit
│   │   │   ├── analytics/       # BI computation (never persisted)
│   │   │   ├── ai_advisor/      # LLMClient protocol + OpenRouter
│   │   │   └── auth/            # JWT login, route dependencies
│   │   ├── shared/
│   │   │   ├── config/          # pydantic-settings (reads .env)
│   │   │   ├── database/        # SQLAlchemy engine + session
│   │   │   └── exceptions/      # Domain exceptions + FastAPI handlers
│   │   └── main.py
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   └── src/
│       ├── api/                 # Axios client + per-context API functions
│       ├── components/          # Layout, Navigation, AdminLayout, ui/
│       ├── contexts/            # AuthContext (JWT in localStorage)
│       └── features/
│           ├── order/           # Pizza builder
│           ├── checkout/        # Payment + receipt
│           ├── analytics/       # Dashboard + Recharts
│           ├── ai/              # AI Advisor
│           └── admin/           # Login page
├── tests/
│   └── contexts/                # Mirrors backend context structure
│       ├── reference/           # 15 tests
│       ├── order/               # 30 tests
│       ├── checkout/            # 28 tests
│       ├── analytics/           # 23 tests
│       └── ai_advisor/          # 22 tests
├── docs/                        # 14 architecture documents
└── scripts/
    ├── menu.csv                 # Seed menu data
    └── seed_mock_data.py        # 60-day mock order history
```

---

## Running locally

### Prerequisites

- Python 3.12+
- Node.js 18+
- An [OpenRouter](https://openrouter.ai) API key

### 1. Clone the repo

```bash
git clone https://github.com/das0777/PIZZA-FLOW.git
cd PIZZA-FLOW
```

### 2. Backend setup

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env — set your OPENROUTER_API_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY
```

`.env` reference:

```env
DATABASE_URL=sqlite:///./pizzaflow_local.db

OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

MENU_FILE_PATH=/absolute/path/to/scripts/menu.csv

ADMIN_USERNAME=admin
ADMIN_PASSWORD=yourpassword
SECRET_KEY=your-random-secret-key
```

Start the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Optionally seed 60 days of realistic mock data for the AI Advisor:

```bash
python ../scripts/seed_mock_data.py
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` → `http://localhost:8001` automatically.

### 4. Access the app

| Portal | URL | Auth |
|---|---|---|
| Customer Portal | http://localhost:5173/order | Public |
| Admin Login | http://localhost:5173/admin/login | — |
| Analytics | http://localhost:5173/admin/analytics | JWT required |
| AI Advisor | http://localhost:5173/admin/ai | JWT required |
| API Docs | http://localhost:8001/docs | — |

---

## Running tests

```bash
cd backend
pytest ../tests/ -v
```

```
tests/contexts/reference/    15 passed
tests/contexts/order/        30 passed
tests/contexts/checkout/     28 passed
tests/contexts/analytics/    23 passed
tests/contexts/ai_advisor/   22 passed
─────────────────────────────────────
118 passed, 0 failed
```

Tests use in-memory SQLite with `StaticPool` — no test database files, no external services. The LLM client is mocked in all AI Advisor tests.

---

## API overview

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/` | — | Health check |
| `GET` | `/menu` | — | List all menu items |
| `POST` | `/orders` | — | Create a new order |
| `GET` | `/orders/{id}` | — | Get order details |
| `POST` | `/checkout/{order_id}` | — | Complete checkout (atomic) |
| `GET` | `/analytics` | JWT | Business Intelligence Model |
| `POST` | `/ai/query` | JWT | Ask the AI Advisor |
| `POST` | `/auth/login` | — | Get JWT token |

Full schema at `/docs` (Swagger UI) when running locally.

---

## Deploying to Vercel

Frontend and backend deploy as **two separate Vercel projects**, each with its own domain.

- **Backend**: Root Directory = `backend`. Vercel auto-detects `app/main.py` as a zero-config FastAPI app (no `api/` folder or rewrites needed) — it becomes a single Vercel Function serving `/`, `/menu`, `/orders`, `/auth/login`, etc. directly at the project's own domain. `backend/vercel.json` sets `maxDuration` and `includeFiles` (the `scripts/*.txt` seed data isn't reached via a normal `import`, so it must be explicitly bundled).
- **Frontend**: Root Directory = `frontend`. Standard Vite static build (framework auto-detected). `frontend/vercel.json` adds a catch-all rewrite to `index.html` so client-side routes (e.g. `/admin/analytics`) don't 404 on a hard refresh.

Because they're on different domains, the frontend talks to the backend over an absolute URL (`VITE_API_BASE_URL`), and the backend's CORS must allow the frontend's domain.

### 1. Create both projects

From the repo root, link each subfolder as its own project (or import the repo twice in the dashboard, setting Root Directory each time):

```bash
cd backend && vercel link     # Root Directory: backend
cd ../frontend && vercel link # Root Directory: frontend
```

### 2. Set environment variables

**Backend project** (Project Settings → Environment Variables):

| Variable | Notes |
|---|---|
| `DATABASE_URL` | Use a pooled Postgres connection string (e.g. Supabase's pgbouncer/transaction pooler on port `6543`) — serverless functions open/close connections frequently |
| `OPENROUTER_API_KEY` | |
| `OPENROUTER_MODEL` | e.g. `openai/gpt-4o-mini` |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` |
| `MENU_FILE_PATH` | `scripts/Types_of_Pizza.txt` (resolved relative to `backend/` at runtime) |
| `BASE_FILE_PATH` | `scripts/Types_of_Base.txt` |
| `TOPPING_FILE_PATH` | `scripts/Types_of_Toppings.txt` |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Admin portal login |
| `SECRET_KEY` | JWT signing secret |
| `CORS_ORIGINS` | `["https://<your-frontend-domain>.vercel.app"]` — must include the frontend's real deployed URL |

**Frontend project**:

| Variable | Notes |
|---|---|
| `VITE_API_BASE_URL` | `https://<your-backend-domain>.vercel.app` (no trailing slash, no `/api` — the backend's own routes are unprefixed) |

### 3. Deploy each project

```bash
cd backend && vercel deploy --prod
cd ../frontend && vercel deploy --prod
```

Deploy the backend first so you know its URL for the frontend's `VITE_API_BASE_URL`. Once both are up, `GET https://<backend-domain>/menu` should return the seeded menu, and `https://<frontend-domain>/` should load and call it with no CORS errors.

---

## Design decisions worth noting

**Why is the BI Model never persisted?**  
Analytics are computed fresh on every request from the immutable transaction record (bills + payments). This means filters (date range, customer, payment method, pizza) work correctly without maintaining a separate aggregation table. Principle 9.

**Why does the AI receive structured text instead of raw database rows?**  
The LLM's role is reasoning, not calculation. Passing raw data would risk hallucinated arithmetic. `AnalyticsService` computes every number; `AIService` formats it as prose and passes it to the LLM as a read-only briefing. The LLM interprets and advises — it never calculates.

**Why is Checkout atomic?**  
`Order → Paid`, `Bill`, and `Payment` are written in a single database transaction. If payment recording fails, the order stays `Pending`. There is no half-paid state. Principle 8 / Rule 8.

**Why are historical prices captured at checkout time?**  
Menu prices can change. The `unit_price` on `OrderItem` and `gst_rate` on `Bill` are captured at the moment of transaction — not looked up later. This ensures bills are legally accurate even after price updates. Principle 18.

---

## What's next (v2 ideas)

- Multi-item order editing before checkout
- Customer order history and loyalty tracking
- Scheduled weekly AI digest report
- Push notifications for new orders

---

## Author

Built by **Rajan (Saptarshi Das)** as a structured exercise in software architecture methodology — from business problem discovery through bounded context design to full implementation.

- GitHub: [@das0777](https://github.com/das0777)
- Email: saptarshidasrick@gmail.com
