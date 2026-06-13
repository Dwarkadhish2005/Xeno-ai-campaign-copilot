# Xeno AI Campaign Copilot

**AI-Native Customer Engagement Platform** — A microservices-based system for intelligent campaign planning, audience segmentation, and multi-channel communication with Groq AI integration.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Component Roles](#component-roles)
5. [Project Workflow](#project-workflow)
6. [Directory Structure](#directory-structure)
7. [Setup & Installation](#setup--installation)
8. [Running the Project](#running-the-project)
9. [API Endpoints](#api-endpoints)
10. [Database Schema](#database-schema)
11. [Development Guide](#development-guide)

---

## Project Overview

### Purpose
Xeno AI Campaign Copilot is an intelligent marketing platform that uses agentic AI to:
- Analyze customer behavior and segment audiences
- Generate targeted campaign strategies using Groq LLMs
- Execute multi-channel communications (Email, SMS, WhatsApp)
- Track campaign performance and ROI
- Provide real-time analytics dashboards

### Key Features
- **CSV Data Ingestion:** Upload customer and order data with row-level validation
- **Customer Intelligence:** Automatic profile generation, segmentation, and analytics
- **AI-Powered Campaigns:** Generate campaign strategies and personalized messages using Groq API
- **Multi-Channel Execution:** Simulate message delivery across Email, SMS, and WhatsApp
- **Analytics & Insights:** Track conversions, engagement metrics, and campaign performance
- **Responsive UI:** Modern Next.js dashboard for campaign management and reporting

### Deployment Targets
- **Frontend:** Vercel (Next.js)
- **Backend Services:** Render (FastAPI)
- **Database:** Supabase PostgreSQL

---

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client Layer                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Next.js Frontend (Port 3000)                  │  │
│  │  - Dashboard, Campaign Planner, Analytics, Upload UI      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             ▲                     │
                             │                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API Gateway Layer                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         FastAPI Main Backend (Port 8000)                  │  │
│  │  - Health Check, Upload (CSV), Intelligence, Analytics    │  │
│  │  - Campaign Planning, Audience Management                 │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                      ▲                    ▼
         ┌────────────┴────────────┐      │
         │                         │      ▼
         │                    ┌────────────────────┐
         │                    │  Groq API Layer    │
         │                    │  (AI Reasoning)    │
         │                    │  llama-3.3-70b    │
         │                    └────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Service Layer                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │      FastAPI Channel Service (Port 8001)                  │  │
│  │  - Message Simulation & Delivery                          │  │
│  │  - Communication Log Tracking                             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         ▲                                │
         │                                ▼
         └────────────────────────────────┐
                                          │
                                          ▼
                    ┌─────────────────────────────────┐
                    │  PostgreSQL Database            │
                    │  (Supabase)                     │
                    │  - Customers, Orders            │
                    │  - Campaigns, Audiences         │
                    │  - Communication Logs, Profiles │
                    │  - Conversions, Analytics       │
                    └─────────────────────────────────┘
```

### Microservices Architecture

| Service | Port | Role | Technology |
|---------|------|------|-----------|
| **Main Backend** | 8000 | API, Business Logic, AI Integration | FastAPI, SQLAlchemy, Groq |
| **Channel Service** | 8001 | Message Simulation, Delivery | FastAPI, SQLAlchemy |
| **Frontend** | 3000 | User Interface, Dashboards | Next.js, TypeScript, Tailwind |
| **Database** | 5432 | Data Persistence | PostgreSQL (Supabase) |

---

## Technology Stack

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** ShadCN UI
- **HTTP Client:** Axios
- **Charts:** Recharts (Analytics)

### Backend
- **Framework:** FastAPI (Async)
- **Database ORM:** SQLAlchemy 2.0 (with asyncpg for async)
- **Migrations:** Alembic
- **Data Validation:** Pydantic v2
- **Data Processing:** Pandas
- **Task Management:** FastAPI BackgroundTasks
- **HTTP:** httpx, requests
- **Retry Logic:** Tenacity

### AI / ML
- **LLM API:** Groq (llama-3.3-70b-versatile)
- **JSON Output:** Structured JSON responses from AI

### Database
- **System:** PostgreSQL 13+ (Supabase)
- **Connection Pool:** SQLAlchemy async session pool (5-10 connections)
- **SSL:** Required for remote connections

### DevOps
- **Environment:** Python 3.10+, Node.js 18+
- **Package Managers:** pip (Python), npm (Node)
- **Async Driver:** asyncpg (PostgreSQL for async)

---

## Component Roles

### 1. Frontend (Next.js)

**Location:** `frontend/`

**Role:** 
- User-facing web application for campaign management, data upload, and analytics.

**Key Pages:**
- **Dashboard** (`app/page.tsx`) — Overview, recent campaigns, key metrics
- **Campaigns** (`app/campaigns/page.tsx`) — List, create, edit campaigns
- **Campaign Detail** (`app/campaigns/[id]/page.tsx`) — View campaign details, performance
- **Planner** (`app/planner/page.tsx`) — AI-powered campaign planning interface
- **Analytics** (`app/analytics/page.tsx`) — Charts, conversions, engagement metrics
- **Upload** (`app/upload/page.tsx`) — CSV upload for customers and orders

**Components:**
- `Sidebar.tsx` — Navigation sidebar
- `Toast.tsx` — Notification system

**Services:**
- `lib/api.ts` — HTTP client wrapper for backend APIs
- `lib/utils.ts` — Utility functions

**Responsibilities:**
- Render dynamic UI based on real-time data from backend
- Handle user input and form validation
- Display analytics and campaign reports
- Provide feedback through toast notifications

---

### 2. Main Backend (FastAPI)

**Location:** `backend/app/`

**Role:**
- Core API, business logic, AI integration, and database operations.

**Key Modules:**

#### `config.py`
- Loads environment variables using Pydantic `BaseSettings`
- Auto-converts sync `postgresql://` URLs to `postgresql+asyncpg://` for async driver
- Defines `DATABASE_URL`, `GROQ_API_KEY`, `CHANNEL_SERVICE_URL`, `ENVIRONMENT`

#### `database.py`
- Creates async SQLAlchemy engine with connection pooling
- Provides `async_session_maker` for dependency injection
- `get_async_session()` — Async context manager for DB sessions (auto-commit/rollback)

#### `base.py`
- SQLAlchemy `DeclarativeBase` for ORM models

#### `models.py`
- **Customer** — User profiles (name, email, phone, city, signup_date)
- **Order** — Purchase records (customer_id, amount, order_date, category, status)
- **CustomerProfile** — Aggregated metrics (total_orders, total_spend, segment, etc.)
- **Campaign** — Campaign definitions (name, channel, strategy, message_template, status)
- **CampaignAudience** — Many-to-many: campaigns ↔ customers
- **CommunicationLog** — Message delivery tracking (channel, status, timestamps)
- **CampaignConversion** — Conversion attribution (campaign → order → revenue)

#### `main.py`
- FastAPI app setup with CORS configuration
- `/health` endpoint for monitoring
- Route imports from `routers/`

#### `routers/`

**`upload.py`**
- `POST /upload/customers` — CSV ingest with validation, batch insert (1000 rows/batch)
- `POST /upload/orders` — CSV ingest with FK validation, batch insert
- Returns data quality reports

**`intelligence.py`**
- `POST /intelligence/generate-profiles` — Compute aggregations from orders, upsert to `customer_profiles`
- `GET /intelligence/profiles` — Paginated profiles with filtering (segment, min_spend, days_inactive)
- `GET /intelligence/profiles/{customer_id}` — Single profile + recent orders
- `GET /intelligence/segments` — Segment distribution counts
- `GET /intelligence/summary` — Business summary, top spenders

**`campaigns.py`**
- `POST /campaigns` — Create campaign
- `GET /campaigns` — List campaigns
- `GET /campaigns/{id}` — Campaign detail
- `PUT /campaigns/{id}` — Update campaign
- `DELETE /campaigns/{id}` — Delete campaign

**`analytics.py`**
- `GET /analytics/summary` — Campaign performance overview
- `GET /analytics/conversions` — Conversion analytics
- `GET /analytics/engagement` — Engagement by channel

**`audience.py`**
- `POST /audience/segment` — Segment customers by filters
- `GET /audience/{segment}` — List customers in segment

#### `services/`

**`groq_service.py`**
- Wraps Groq API calls for campaign planning
- `generate_campaign_strategy()` — AI reasoning for campaign approach
- `generate_message()` — Personalized message generation
- Implements retry logic (3 attempts, exponential backoff)
- Validates JSON output against schemas

**`audience_service.py`**
- Segment logic: RFM (Recency, Frequency, Monetary)
- Filter by segment, spend, and engagement

**`executor_service.py`**
- Campaign execution orchestration
- Calls Channel Service to send messages

**`channel_client.py`**
- HTTP client for Channel Service API

**Responsibilities:**
- Accept and validate HTTP requests
- Manage database transactions
- Call Groq API for AI reasoning
- Orchestrate multi-service workflows
- Return structured JSON responses

---

### 3. Channel Service (FastAPI)

**Location:** `channel-service/app/`

**Role:**
- Isolated microservice for message simulation and delivery tracking.

**Key Modules:**

#### `config.py`
- Environment variables: `DATABASE_URL`, `MAIN_BACKEND_URL`, `ENVIRONMENT`

#### `database.py`
- Similar async setup as main backend

#### `main.py`
- FastAPI app with Channel Service routes

#### `routers/messages.py`
- `POST /messages/send` — Simulate message send across channels (Email, SMS, WhatsApp)
- `GET /messages/{id}` — Message delivery status
- `GET /messages/logs` — Communication logs

**Responsibilities:**
- Simulate realistic message delivery
- Track delivery status (sent, delivered, failed)
- Log all communications for audit trail
- Provide stateless message handling (can scale horizontally)

---

### 4. Database (PostgreSQL)

**Location:** Supabase (Remote)

**Role:**
- Central data store for all application data with ACID guarantees.

**Tables:**
- `customers` — Customer profiles
- `orders` — Purchase transactions
- `customer_profiles` — Computed metrics and segments
- `campaigns` — Campaign definitions
- `campaign_audience` — Campaign-customer associations
- `communication_logs` — All sent messages
- `campaign_conversions` — Attribution tracking

**Key Features:**
- Connection pooling via PgBouncer (optional)
- Row-level security for multi-tenant scenarios (optional future)
- Full-text search indices (optional future)
- Partitioning on time-series tables for performance (optional future)

---

## Project Workflow

### End-to-End Campaign Flow

```
1. DATA INGESTION
   ├─ User uploads customers.csv via Frontend
   ├─ Backend validates and inserts into `customers` table
   ├─ User uploads orders.csv via Frontend
   └─ Backend validates FK constraints and inserts into `orders` table

2. INTELLIGENCE GENERATION
   ├─ Backend reads all orders, computes aggregations
   ├─ RFM segmentation applied
   └─ Results upserted into `customer_profiles` table

3. AUDIENCE SEGMENTATION
   ├─ User selects filters (segment, spend, recency) on Frontend
   ├─ Backend queries `customers` + `customer_profiles`
   └─ Returns filtered audience

4. CAMPAIGN PLANNING (AI)
   ├─ User defines business goal, target audience, channel on Frontend
   ├─ Backend sends context to Groq API
   ├─ Groq returns campaign strategy and message template
   └─ Backend stores in `campaigns` table

5. CAMPAIGN EXECUTION
   ├─ Backend creates `campaign_audience` entries for selected customers
   ├─ Backend calls Channel Service to send messages
   ├─ Channel Service simulates delivery, logs to `communication_logs`
   └─ Frontend polls for status updates

6. CONVERSION TRACKING
   ├─ New orders ingested (repeat of step 2)
   ├─ Backend attributes orders to campaigns within attribution window
   ├─ Results stored in `campaign_conversions` table
   └─ Frontend displays ROI and campaign performance

7. ANALYTICS & REPORTING
   ├─ Frontend queries analytics endpoints
   ├─ Backend aggregates conversions, engagement, revenue by campaign
   └─ Dashboards display KPIs and trends
```

### Data Flow Diagram

```
User Input (Frontend)
    │
    ├─→ CSV Upload → Backend Upload Handler → Database
    │
    ├─→ Campaign Config → Backend Campaign Router → Groq API
    │                        ↓
    │                   Groq Response
    │                        ↓
    │                   Backend stores
    │
    └─→ Execute Campaign → Backend Executor → Channel Service → Simulated Send
                                                    ↓
                                            Communication Log
                                                    ↓
                                            Database
                                                    ↓
                                            Frontend Analytics
```

---

## Directory Structure

```
xeno-ai-campaign-copilot/
│
├── README.md                           # Project documentation (this file)
├── .env                                # Backend environment variables
│
├── backend/                            # Main FastAPI Backend
│   ├── .env                           # DB credentials, API keys
│   ├── requirements.txt               # Python dependencies
│   ├── main.py                        # Sync connection test (legacy)
│   ├── test_db_connection.py          # Async DB connection test
│   ├── test_full_project.py           # Integration tests
│   ├── alembic.ini                    # Migration config
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app initialization
│   │   ├── config.py                  # Settings (Pydantic v2)
│   │   ├── database.py                # SQLAlchemy async engine
│   │   ├── base.py                    # DeclarativeBase for ORM
│   │   ├── models.py                  # SQLAlchemy models
│   │   ├── schemas.py                 # Pydantic request/response models
│   │   ├── dependencies.py            # FastAPI dependency injection
│   │   │
│   │   ├── routers/
│   │   │   ├── upload.py             # CSV ingestion endpoints
│   │   │   ├── intelligence.py       # Profile & segment generation
│   │   │   ├── campaigns.py          # Campaign CRUD
│   │   │   ├── analytics.py          # Analytics endpoints
│   │   │   └── audience.py           # Audience segmentation
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── groq_service.py       # Groq API wrapper
│   │       ├── audience_service.py   # RFM segmentation logic
│   │       ├── executor_service.py   # Campaign execution
│   │       └── channel_client.py     # Channel Service HTTP client
│   │
│   └── alembic/
│       ├── env.py                    # Alembic async config
│       ├── script.py.mako            # Migration template
│       └── versions/                 # Migration files
│           ├── 545881a53ba8_initial_models.py
│           └── 90086082b1ea_initial_models_v2.py
│
├── channel-service/                   # Message Simulation Service
│   ├── requirements.txt              # Python dependencies
│   ├── .env                          # DB credentials
│   │
│   └── app/
│       ├── __init__.py
│       ├── main.py                   # FastAPI app
│       ├── config.py                 # Settings
│       ├── database.py               # SQLAlchemy async engine
│       │
│       └── routers/
│           └── messages.py           # Message simulation endpoints
│
├── frontend/                          # Next.js Frontend
│   ├── package.json                  # Node.js dependencies
│   ├── next.config.ts                # Next.js config
│   ├── tsconfig.json                 # TypeScript config
│   ├── tailwind.config.ts            # Tailwind CSS config
│   ├── postcss.config.mjs            # PostCSS config
│   │
│   ├── app/
│   │   ├── globals.css               # Global styles
│   │   ├── layout.tsx                # Root layout
│   │   ├── page.tsx                  # Dashboard home
│   │   ├── analytics/
│   │   │   └── page.tsx             # Analytics dashboard
│   │   ├── campaigns/
│   │   │   ├── page.tsx             # Campaigns list
│   │   │   └── [id]/
│   │   │       └── page.tsx         # Campaign detail
│   │   ├── planner/
│   │   │   └── page.tsx             # AI campaign planner
│   │   └── upload/
│   │       └── page.tsx             # Data upload page
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   └── Sidebar.tsx           # Navigation
│   │   └── ui/
│   │       └── Toast.tsx             # Notifications
│   │
│   ├── lib/
│   │   ├── api.ts                    # Axios wrapper
│   │   └── utils.ts                  # Utility functions
│   │
│   └── public/                       # Static assets
│
└── dataset/                           # Data generation utilities
    ├── generate_dataset.py           # Create sample data
    ├── validate_data.py              # Validate CSV format
    └── output/
        ├── customers.csv
        ├── orders.csv
        └── customer_profiles.csv
```

---

## Setup & Installation

### Prerequisites
- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **PostgreSQL 13+** (Supabase or local instance)
- **Groq API Key** from [Groq Console](https://console.groq.com)

### Step 1: Clone & Navigate

```bash
cd c:\Dwarka\xeno ai campaign copilot
```

### Step 2: Backend Setup

#### Create Virtual Environment
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment
Create `backend/.env`:
```env
# Database (use sync postgresql:// URL for Alembic compatibility)
DATABASE_URL=postgresql://dbuser:dbpass@db.host:5432/xeno_campaign

# AI & Services
GROQ_API_KEY=your_groq_api_key_here
CHANNEL_SERVICE_URL=http://localhost:8001

# Environment
ENVIRONMENT=development
```

**Notes:**
- Replace `dbuser`, `dbpass`, `db.host`, `xeno_campaign` with your Supabase credentials
- The app automatically converts `postgresql://` to `postgresql+asyncpg://` for async runtime
- For Supabase: find credentials in Project Settings → Database → Connection String

#### Run Migrations
```powershell
cd backend
alembic upgrade head
```

#### Test Database Connection
```powershell
python test_db_connection.py
```

Expected output: `DB connection OK`

### Step 3: Channel Service Setup

```powershell
cd ..\channel-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `channel-service/.env`:
```env
DATABASE_URL=postgresql://dbuser:dbpass@db.host:5432/xeno_campaign
MAIN_BACKEND_URL=http://localhost:8000
ENVIRONMENT=development
```

### Step 4: Frontend Setup

```powershell
cd ..\frontend
npm install
```

Create `frontend/.env.local` (if needed for API base URL):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Running the Project

### Terminal Setup (4 Terminals Required)

Open **4 separate PowerShell terminals** in the project root.

### Terminal 1: Main Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
Uvicorn running on http://0.0.0.0:8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Terminal 2: Channel Service

```powershell
cd channel-service
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Expected output:
```
Uvicorn running on http://0.0.0.0:8001
```

### Terminal 3: Frontend

```powershell
cd frontend
npm run dev
```

Expected output:
```
Local: http://localhost:3000
```

### Terminal 4: Monitoring (Optional)

```powershell
cd backend
# Monitor database connection or logs
tail -f .env  # or check recent API calls via logs
```

---

## API Endpoints

### Health & Status

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/health` | System health check |

### Data Upload

| Method | Endpoint | Purpose | Body |
|--------|----------|---------|------|
| `POST` | `/upload/customers` | Ingest customers CSV | `FormData: file` |
| `POST` | `/upload/orders` | Ingest orders CSV | `FormData: file` |

### Intelligence

| Method | Endpoint | Purpose | Query Params |
|--------|----------|---------|--------------|
| `POST` | `/intelligence/generate-profiles` | Compute customer profiles | — |
| `GET` | `/intelligence/profiles` | List profiles (paginated) | `page`, `limit`, `segment`, `min_spend`, `max_days_inactive` |
| `GET` | `/intelligence/profiles/{customer_id}` | Single customer profile | — |
| `GET` | `/intelligence/segments` | Segment distribution | — |
| `GET` | `/intelligence/summary` | Business summary | — |

### Campaigns

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/campaigns` | Create campaign |
| `GET` | `/campaigns` | List campaigns |
| `GET` | `/campaigns/{id}` | Campaign detail |
| `PUT` | `/campaigns/{id}` | Update campaign |
| `DELETE` | `/campaigns/{id}` | Delete campaign |

### Analytics

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/analytics/summary` | Campaign performance summary |
| `GET` | `/analytics/conversions` | Conversion analytics |
| `GET` | `/analytics/engagement` | Engagement by channel |

### Audience

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/audience/segment` | Segment customers by filters |
| `GET` | `/audience/{segment}` | List customers in segment |

### Channel Service

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/messages/send` | Send message (simulate) |
| `GET` | `/messages/{id}` | Message delivery status |
| `GET` | `/messages/logs` | Communication logs |

---

## Database Schema

### Tables Overview

#### `customers`
- `id` (PK) — Auto-incrementing customer ID
- `name` — Customer full name
- `email` — Unique email address
- `phone` — Optional E.164 formatted phone
- `city` — Optional city
- `signup_date` — Account creation date
- `created_at`, `updated_at` — Timestamps

#### `orders`
- `id` (PK)
- `customer_id` (FK → customers) — ON DELETE CASCADE
- `amount` — Purchase amount (DECIMAL)
- `order_date` — Purchase timestamp
- `category` — Product category
- `status` — Order status (completed, pending, etc.)
- `created_at`, `updated_at`

#### `customer_profiles`
- `id` (PK)
- `customer_id` (FK → customers, unique)
- `total_orders` — Count of orders
- `total_spend` — Sum of amounts
- `average_order_value` — avg(amount)
- `last_purchase_date` — Max order_date
- `days_since_last_purchase` — Days elapsed
- `purchase_frequency` — Orders per day (calculated)
- `customer_segment` — RFM segment (e.g., "High Value", "At Risk")
- `created_at`, `updated_at`

#### `campaigns`
- `id` (PK)
- `name` — Campaign name
- `audience_name` — Target audience label
- `filters` — JSON: filter criteria
- `channel` — Email, SMS, or WhatsApp
- `strategy` — Campaign approach (from Groq)
- `message_template` — Message body template
- `subject_line` — Email subject (if applicable)
- `status` — draft, scheduled, active, completed, paused
- `audience_size` — Count of target customers
- `business_goal` — Marketing objective
- `ai_reasoning` — Groq reasoning trace
- `created_at`, `updated_at`

#### `campaign_audience`
- `id` (PK)
- `campaign_id` (FK → campaigns) — ON DELETE CASCADE
- `customer_id` (FK → customers) — ON DELETE CASCADE
- `created_at`

#### `communication_logs`
- `id` (PK)
- `campaign_id` (FK → campaigns, nullable)
- `customer_id` (FK → customers, nullable)
- `channel` — Email, SMS, WhatsApp
- `message` — Base message
- `personalized_message` — Rendered message
- `status` — sent, delivered, failed, opened, clicked
- `sent_at`, `delivered_at`, `opened_at`, `clicked_at`, `failed_at`
- `error_message` — Failure reason
- `metadata` — JSON metadata

#### `campaign_conversions`
- `id` (PK)
- `campaign_id` (FK → campaigns, nullable)
- `customer_id` (FK → customers, nullable)
- `communication_log_id` (FK → communication_logs, nullable)
- `order_id` (FK → orders, nullable)
- `converted_at` — Conversion timestamp
- `conversion_value` — Revenue from converted order
- `attribution_window_days` — Days after send to attribute (default: 7)

---

## Development Guide

### Code Quality Standards

#### Type Safety
- **Backend:** Pydantic v2 for all request/response models; SQLAlchemy type hints with `Mapped[]`
- **Frontend:** Strict TypeScript (no `any` unless justified)

#### Error Handling
All endpoints wrapped in try/catch with structured responses:

```json
{
  "success": false,
  "data": null,
  "message": "Error description"
}
```

#### Logging
- **Backend:** Use Python logging module; log at `DEBUG`, `INFO`, `WARNING`, `ERROR` levels
- **Frontend:** Console.log for dev; structured logging for prod (optional)

#### Environment Variables
- Never hardcode secrets or URLs
- Use `.env` files locally; environment variables in CI/CD
- Always use Pydantic `BaseSettings` for runtime config validation

#### Async / Await
- **Backend:** All I/O (DB, HTTP) must use `async/await`
- Use `select()` syntax for SQLAlchemy v2 queries
- Example:
  ```python
  stmt = select(Customer).where(Customer.email == email)
  result = await session.execute(stmt)
  customer = result.scalars().first()
  ```

#### Testing
- Unit tests for services (mocking DB/API)
- Integration tests for endpoints (live DB)
- Use `pytest` for test runner

#### API Standards
- RESTful conventions (GET, POST, PUT, DELETE)
- Consistent naming (kebab-case for URLs, snake_case for JSON)
- Version URLs if breaking changes needed (e.g., `/api/v1/campaigns`)

### Adding New Endpoints

1. **Create Pydantic schema** in `backend/app/schemas.py`
   ```python
   class NewFeatureRequest(BaseModel):
       name: str
       value: int
   ```

2. **Add route** in `backend/app/routers/new_feature.py`
   ```python
   @router.post("/new-feature")
   async def create_feature(req: NewFeatureRequest, session: AsyncSession = Depends(get_async_session)):
       # Logic here
       return {"success": True, "data": result}
   ```

3. **Include router** in `backend/app/main.py`
   ```python
   app.include_router(new_feature.router, prefix="/api", tags=["features"])
   ```

4. **Frontend call** in `frontend/lib/api.ts`
   ```typescript
   export const createFeature = (data) => 
     api.post("/new-feature", data);
   ```

### Database Migration Workflow

1. **Modify model** in `backend/app/models.py`
2. **Generate migration:**
   ```bash
   alembic revision --autogenerate -m "descriptive message"
   ```
3. **Review** generated file in `alembic/versions/`
4. **Apply:**
   ```bash
   alembic upgrade head
   ```
5. **Rollback (if needed):**
   ```bash
   alembic downgrade -1
   ```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| DB connection fails | Check `DATABASE_URL` format, ensure Supabase is reachable, verify SSL settings |
| Alembic errors | Ensure sync `postgresql://` URL in `.env`; async URL will cause issues |
| Missing `asyncpg` module | `pip install asyncpg` in backend venv |
| Frontend API calls fail | Check CORS settings in `backend/app/main.py`; verify backend port is 8000 |
| Channel Service not found | Ensure `CHANNEL_SERVICE_URL` in `backend/.env` points to correct host/port |
| Groq API errors | Check `GROQ_API_KEY` is valid; monitor rate limits; retry logic will auto-backoff |

### Useful Commands

**Backend**
```bash
# Activate venv
.\.venv\Scripts\Activate.ps1

# Run tests
pytest backend/tests/

# Check migrations
alembic history

# Reset DB (careful!)
alembic downgrade base
alembic upgrade head

# Lint
pylint app/
```

**Frontend**
```bash
# Build
npm run build

# Export static
npm run export

# Lint
npm run lint

# Format
npm run format
```

---

## Deployment

### Frontend (Vercel)
1. Push code to GitHub
2. Connect repo to Vercel
3. Set `NEXT_PUBLIC_API_URL` env var to production backend URL
4. Auto-deploy on push

### Backend (Render)
1. Create new Web Service on Render
2. Connect GitHub repo
3. Set env vars: `DATABASE_URL`, `GROQ_API_KEY`, `CHANNEL_SERVICE_URL`, `ENVIRONMENT=production`
4. Build command: `pip install -r backend/requirements.txt`
5. Start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Database (Supabase)
1. Create new project on Supabase
2. Get connection string from Project Settings → Database → Connection String
3. Use `postgresql://` format for Alembic migrations
4. Run migrations: `alembic upgrade head`

---

## Support & Troubleshooting

### Logs Location
- **Backend:** stdout from `uvicorn` terminal
- **Frontend:** Browser console (F12)
- **Database:** Supabase dashboard → Logs

### Debug Mode
Set `ENVIRONMENT=development` in `.env`:
- Backend will log all SQL queries
- API responses will include trace info

### Reset Everything
```bash
# Backend
cd backend
alembic downgrade base  # Drop all tables
alembic upgrade head    # Recreate from scratch

# Frontend
cd frontend
rm -r .next node_modules
npm install
npm run dev
```

---

## License

Proprietary — Xeno AI Campaign Copilot

---

## Contact & Support

For issues or questions, refer to the project documentation or contact the development team.

**Happy campaigning! 🚀**
