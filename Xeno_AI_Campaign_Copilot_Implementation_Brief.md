# Project Xeno AI Campaign Copilot
## Agentic AI Implementation Brief
### Version 2.0 | Phase-by-Phase Build Guide

---
MVP MUST NOT INCLUDE

Authentication
RBAC
OAuth
Redis
Kafka
RabbitMQ
Celery
Docker Swarm
Kubernetes
Vector Databases
FAISS
Pinecone
Chroma
Embeddings
RAG
LangGraph
CrewAI
Multi-Agent Systems
Real WhatsApp APIs
Real SMS Providers
Real Email Providers


## 1. MASTER PROJECT OVERVIEW

**Project Name:** Xeno AI Campaign Copilot  
**Type:** AI-Native Customer Engagement Platform  
**Architecture:** Microservices (3 Services + 1 Database)  
**Deployment Targets:** Vercel (Frontend), Render (Backend + Channel Service), Supabase (Database)

### 1.1 Architecture Diagram
```
+-----------------+     +------------------+     +-----------------+
|   Next.js       |---->|   FastAPI        |---->|   PostgreSQL    |
|   (Frontend)    |<----|   (Main Backend) |<----|   (Supabase)    |
+-----------------+     +------------------+     +-----------------+
                               |
                               v
                        +------------------+
                        |   Groq API       |
                        |   (AI Layer)     |
                        +------------------+
                               |
                               v
                        +------------------+
                        |   FastAPI        |
                        |   (Channel       |
                        |    Service)      |
                        +------------------+
```

### 1.2 Tech Stack Summary
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14+ (App Router), TypeScript, Tailwind CSS, ShadCN UI, Axios, Recharts | UI & Dashboards |
| Backend | FastAPI, SQLAlchemy 2.0, Alembic, Pandas, Pydantic v2, BackgroundTasks | API & Business Logic |
| AI Layer | Groq API (llama-3.3-70b-versatile) | Campaign Planning & Generation |
| Database | PostgreSQL (Supabase) | Data Persistence |
| Channel Service | FastAPI (Separate Deployment) | Message Simulation |

---

## 2. GLOBAL RULES FOR ALL AGENTS

### 2.1 Code Quality Standards
- **Type Safety:** Strict typing everywhere (TypeScript frontend, Pydantic v2 backend)
- **Error Handling:** Every API call wrapped in try/catch with structured error responses
- **Logging:** Structured JSON logging for all services
- **Environment Variables:** NEVER hardcode secrets; use `.env` files with `pydantic-settings`
- **CORS:** Configure properly for cross-service communication
- **Async:** Use `async/await` throughout FastAPI services; SQLAlchemy 2.0 async style with `select()`, `await session.execute()`, `result.scalars().all()`

### 2.2 Database Rules
- All tables must have `id` (SERIAL PK), `created_at`, `updated_at`
- Use Alembic for ALL schema migrations
- Use SQLAlchemy 2.0 style: `DeclarativeBase`, `Mapped[]` types, `select()` syntax
- Foreign keys with `ON DELETE CASCADE` where appropriate
- Index on frequently queried fields

### 2.3 API Standards
- RESTful conventions
- Consistent response envelope: `{ "success": bool, "data": any, "message": string }`
- HTTP status codes: 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Server Error)
- Pydantic v2 models for ALL request/response bodies

### 2.4 AI Integration Rules
- Always use structured JSON output from Groq: set `response_format={"type": "json_object"}`
- Include explicit JSON schema instructions in system prompt
- Implement retry logic (3 attempts with exponential backoff)
- Validate AI output against Pydantic schemas before processing
- Use `llama-3.3-70b-versatile` model exclusively

---

## 3. DATASET SPECIFICATION (Pre-Built)

### 3.1 Dataset Files (Already Generated)
The following files are pre-generated and validated. They serve as the foundation for the entire platform.

```
dataset/
├── generate_data.py          # Dataset generator script
├── validate_data.py          # Validation & profiling script
└── output/
    ├── customers.csv         # 1000 customers
    ├── orders.csv            # 9000-12000 orders
    └── customer_profiles.csv # Computed profiles (prototype for DB table)
```

### 3.2 customers.csv Schema
| Column | Type | Description |
|--------|------|-------------|
| customer_id | INTEGER | Primary identifier |
| name | VARCHAR(255) | Customer full name |
| email | VARCHAR(255) | Unique email address |
| phone | VARCHAR(50) | Phone number (E.164 format) |
| city | VARCHAR(100) | Geographic location |
| signup_date | DATE | Account creation date |

**Business Segments Intentionally Built:**
- **VIP Customers (100):** High spend, many orders, recently active -> Reward Campaigns, Premium Offers
- **Dormant Customers (150):** Purchased before, no recent purchases -> Win-back Campaigns, Reactivation Offers
- **Frequent Buyers (200):** Many purchases, medium spend -> Loyalty Campaigns
- **New Customers (100):** Recently joined, few orders -> Onboarding Campaigns
- **At-Risk Customers (150):** Historically active, activity declining -> Retention Campaigns
- **Regular Customers (remaining):** Normal purchasing behavior

### 3.3 orders.csv Schema
| Column | Type | Description |
|--------|------|-------------|
| order_id | INTEGER | Primary identifier |
| customer_id | INTEGER | FK to customers |
| amount | DECIMAL(10,2) | Order total amount |
| order_date | TIMESTAMP | Purchase date |
| category | VARCHAR(100) | Product/service category |

### 3.4 customer_profiles.csv (Prototype for DB Table)
| Column | Type | Description |
|--------|------|-------------|
| customer_id | INTEGER | FK to customers |
| total_orders | INTEGER | Count of all orders |
| total_spend | DECIMAL(12,2) | Sum of all order amounts |
| average_order_value | DECIMAL(10,2) | total_spend / total_orders |
| last_purchase_date | TIMESTAMP | Most recent order date |
| days_since_last_purchase | INTEGER | Days since last_purchase_date |
| purchase_frequency | DECIMAL(5,2) | Orders per month since signup |

### 3.5 Validation Script Capabilities
The `validate_data.py` script verifies:
- Total customer count: 1000
- Total order count: 9000-12000
- Customer-order relationship integrity
- Segment distribution (VIP, Dormant, Frequent, New, At-Risk, Regular)
- Revenue totals and top spenders
- Data quality checks (no orphaned orders, valid dates, positive amounts)

### 3.6 How Dataset Powers Future Phases
| Phase | Uses Dataset For |
|-------|-----------------|
| Phase 2 | Ingest `customers.csv` and `orders.csv` into PostgreSQL |
| Phase 3 | Compute `customer_profiles` table from orders data |
| Phase 4 | AI uses `days_since_last_purchase` to identify dormant users |
| Phase 5 | Filter engine queries `customer_profiles` for audience segmentation |
| Phase 6 | Personalize messages using `name`, `days_since_last_purchase`, `city` |
| Phase 9 | Analytics compares campaign performance against customer profiles |

---

## 4. DATABASE SCHEMA (Master Reference)

Implement ALL tables in Phase 1. Use this as the canonical schema for all phases.

```sql
-- customers
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    city VARCHAR(100),
    signup_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP NOT NULL,
    category VARCHAR(100),
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- customer_profiles (auto-generated in Phase 3 from dataset prototype)
CREATE TABLE customer_profiles (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER UNIQUE REFERENCES customers(id) ON DELETE CASCADE,
    total_orders INTEGER DEFAULT 0,
    total_spend DECIMAL(12,2) DEFAULT 0.00,
    average_order_value DECIMAL(10,2) DEFAULT 0.00,
    last_purchase_date TIMESTAMP,
    days_since_last_purchase INTEGER,
    purchase_frequency DECIMAL(5,2), -- orders per month since signup
    customer_segment VARCHAR(50), -- vip, dormant, frequent, new, at_risk, regular
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- campaigns
CREATE TABLE campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    audience_name VARCHAR(255),
    filters JSONB, -- array of filter objects: [{"field": "days_since_last_purchase", "operator": ">", "value": 30}]
    channel VARCHAR(50) NOT NULL, -- whatsapp, sms, email, rcs
    strategy TEXT,
    message_template TEXT,
    subject_line VARCHAR(255), -- for email campaigns
    status VARCHAR(50) DEFAULT 'draft', -- draft, ready, approved, running, completed, failed
    audience_size INTEGER DEFAULT 0,
    business_goal TEXT, -- original user input
    ai_reasoning TEXT, -- AI explanation for the plan
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- campaign_audience (many-to-many: campaigns <-> customers)
CREATE TABLE campaign_audience (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, customer_id)
);

-- communication_logs
CREATE TABLE communication_logs (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    personalized_message TEXT, -- final message sent to customer
    status VARCHAR(50) DEFAULT 'sent', -- sent, delivered, opened, clicked, failed
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    failed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB -- channel-specific metadata
);

-- campaign_conversions
CREATE TABLE campaign_conversions (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    communication_log_id INTEGER REFERENCES communication_logs(id),
    order_id INTEGER REFERENCES orders(id),
    converted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    conversion_value DECIMAL(10,2),
    attribution_window_days INTEGER DEFAULT 7,
    UNIQUE(campaign_id, customer_id, order_id)
);

-- Indexes for performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_city ON customers(city);
CREATE INDEX idx_customers_signup_date ON customers(signup_date);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_category ON orders(category);
CREATE INDEX idx_customer_profiles_customer_id ON customer_profiles(customer_id);
CREATE INDEX idx_customer_profiles_segment ON customer_profiles(customer_segment);
CREATE INDEX idx_customer_profiles_days_since ON customer_profiles(days_since_last_purchase);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaign_audience_campaign_id ON campaign_audience(campaign_id);
CREATE INDEX idx_communication_logs_campaign_id ON communication_logs(campaign_id);
CREATE INDEX idx_communication_logs_status ON communication_logs(status);
CREATE INDEX idx_communication_logs_customer_id ON communication_logs(customer_id);
CREATE INDEX idx_campaign_conversions_campaign_id ON campaign_conversions(campaign_id);
CREATE INDEX idx_campaign_conversions_customer_id ON campaign_conversions(customer_id);
```

---

## 5. PHASE-BY-PHASE IMPLEMENTATION GUIDE

### PHASE 0: Dataset Generation & Validation (PRE-COMPLETED)
**Status:** Already Done  
**Deliverables:**
- [x] `generate_data.py` creates 1000 customers + 9000-12000 orders with realistic business segments
- [x] `validate_data.py` verifies data quality and generates `customer_profiles.csv`
- [x] Business segments confirmed: VIP (100), Dormant (150), Frequent (200), New (100), At-Risk (150), Regular (remaining)
- [x] `customers.csv`, `orders.csv`, `customer_profiles.csv` ready for ingestion

**Agent Note:** Do NOT regenerate dataset. Use existing files in `dataset/output/`.

---

### PHASE 1: Backend Foundation
**Goal:** Create the project backbone with database connection and project structure.

**Agent Instructions:**
1. Create project structure:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory
│   ├── config.py            # Pydantic v2 settings
│   ├── database.py          # SQLAlchemy 2.0 async engine + session
│   ├── models.py            # All SQLAlchemy 2.0 models (Mapped[] syntax)
│   ├── schemas.py           # All Pydantic v2 schemas
│   ├── dependencies.py      # DB session dependency injection
│   └── routers/
│       ├── __init__.py
│       └── upload.py        # Placeholder for Phase 2
├── alembic/
│   ├── env.py               # Async-compatible Alembic env
│   ├── script.py.mako
│   └── versions/            # Migration files
├── tests/
├── requirements.txt
├── alembic.ini
└── .env.example
```

2. Implement `config.py` using `pydantic-settings` v2:
```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., description="PostgreSQL async URL: postgresql+asyncpg://...")
    GROQ_API_KEY: str = Field(..., description="Groq API key")
    CHANNEL_SERVICE_URL: str = Field(default="http://localhost:8001", description="Channel service URL")
    ENVIRONMENT: str = Field(default="development", description="dev/prod")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

3. Implement `database.py` (SQLAlchemy 2.0 async):
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

4. Implement ALL models from Section 4 in `models.py` using SQLAlchemy 2.0 `Mapped[]` syntax:
```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DECIMAL, DateTime, ForeignKey, JSON, Date
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str | None] = mapped_column(String(100))
    signup_date: Mapped[datetime] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    profile: Mapped["CustomerProfile | None"] = relationship(back_populates="customer", uselist=False)
```

5. Set up Alembic with async support:
   - `alembic.ini`: Use sync `postgresql://` URL for migrations
   - `env.py`: Import `Base` from `app.models`, set `target_metadata = Base.metadata`
   - Generate initial migration: `alembic revision --autogenerate -m "initial_schema"`

6. Create `main.py`:
   - FastAPI app with `lifespan` context manager
   - Health check: `GET /health` returns `{"status": "ok", "timestamp": "..."}`
   - CORS middleware: allow Vercel + Render origins
   - Include router placeholder

**Deliverables:**
- [ ] Backend running locally: `uvicorn app.main:app --reload`
- [ ] Database connected to Supabase
- [ ] Alembic migrations create all tables from Section 4
- [ ] Health check returns 200 OK

**Success Criteria:**
- `curl http://localhost:8000/health` returns `{"status":"ok"}`
- All 7 tables created in Supabase
- No hardcoded credentials anywhere

---

### PHASE 2: Data Ingestion & Validation
**Goal:** Upload pre-generated customer and order datasets into PostgreSQL.

**Agent Instructions:**
1. Create upload endpoints in `app/routers/upload.py`:
   - `POST /upload/customers` - Accepts CSV file (use existing `customers.csv`)
   - `POST /upload/orders` - Accepts CSV file (use existing `orders.csv`)

2. Customer CSV Validation (use Pandas):
   - Check for duplicate emails (within file + against existing DB records)
   - Check for missing emails
   - Validate phone numbers (E.164 regex: `^\+?[1-9]\d{1,14}$`)
   - Validate `signup_date` format (YYYY-MM-DD)
   - Return row-level errors

3. Order CSV Validation:
   - Validate `customer_id` references exist in `customers` table
   - Check for missing `order_date` and `amount`
   - Validate `amount` > 0
   - Validate `order_date` format
   - Return row-level errors

4. Bulk Insert Strategy:
   - Use Pandas `to_sql` with SQLAlchemy engine OR
   - Use `session.execute(insert(Customer).values([...]))` for batches of 1000
   - Process in chunks to avoid memory issues

5. Response Format:
```json
{
  "success": true,
  "data": {
    "total_rows": 1000,
    "valid_rows": 998,
    "invalid_rows": 2,
    "errors": [
      { "row": 5, "field": "email", "message": "Duplicate email: john@example.com" },
      { "row": 12, "field": "customer_id", "message": "Customer ID 999 not found in database" }
    ],
    "inserted_count": 998
  },
  "message": "Upload processed: 998 inserted, 2 errors"
}
```

6. Store files temporarily in `/tmp`, process, then delete.

**Deliverables:**
- [ ] `POST /upload/customers` ingests `customers.csv` with validation
- [ ] `POST /upload/orders` ingests `orders.csv` with validation
- [ ] Data quality report returned for every upload
- [ ] Invalid rows rejected with clear error messages
- [ ] All 1000 customers and 9000-12000 orders successfully stored

**Test Data Reference (from pre-built dataset):**
```csv
# customers.csv
id,name,email,phone,city,signup_date
1,John Doe,john@example.com,+1234567890,New York,2023-01-15
2,Jane Smith,jane@example.com,+1987654321,Los Angeles,2023-02-20
...

# orders.csv
id,customer_id,amount,order_date,category
1,1,150.00,2024-01-15 10:30:00,Electronics
2,1,230.50,2024-02-20 14:15:00,Clothing
...
```

---

### PHASE 3: Customer Intelligence Engine
**Goal:** Transform raw data into customer insights using the pre-built dataset logic.

**Agent Instructions:**
1. Create `app/routers/intelligence.py`

2. Create endpoint `POST /intelligence/generate-profiles`
   - Computes aggregations from `orders` table:
     - `total_orders`: COUNT(orders) per customer
     - `total_spend`: SUM(orders.amount) per customer
     - `average_order_value`: total_spend / NULLIF(total_orders, 0)
     - `last_purchase_date`: MAX(orders.order_date)
     - `days_since_last_purchase`: EXTRACT(DAY FROM CURRENT_TIMESTAMP - last_purchase_date)
     - `purchase_frequency`: total_orders / months_since_signup
     - `customer_segment`: Categorize based on rules:
       - **VIP:** total_spend > threshold AND days_since_last_purchase < 30 AND total_orders > threshold
       - **Dormant:** days_since_last_purchase > 60
       - **Frequent:** total_orders > threshold AND average_order_value > threshold
       - **New:** signup_date within last 30 days
       - **At-Risk:** days_since_last_purchase > 30 AND historically active
       - **Regular:** default

3. Upsert into `customer_profiles` table:
```sql
INSERT INTO customer_profiles (customer_id, total_orders, total_spend, average_order_value, last_purchase_date, days_since_last_purchase, purchase_frequency, customer_segment)
SELECT 
    c.id,
    COUNT(o.id),
    COALESCE(SUM(o.amount), 0),
    COALESCE(AVG(o.amount), 0),
    MAX(o.order_date),
    EXTRACT(DAY FROM CURRENT_TIMESTAMP - MAX(o.order_date)),
    CASE 
        WHEN EXTRACT(MONTH FROM AGE(CURRENT_TIMESTAMP, c.signup_date)) > 0 
        THEN COUNT(o.id)::DECIMAL / NULLIF(EXTRACT(MONTH FROM AGE(CURRENT_TIMESTAMP, c.signup_date)), 0)
        ELSE COUNT(o.id)::DECIMAL
    END,
    CASE
        WHEN COALESCE(SUM(o.amount), 0) > 5000 AND EXTRACT(DAY FROM CURRENT_TIMESTAMP - MAX(o.order_date)) < 30 AND COUNT(o.id) > 10 THEN 'vip'
        WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - MAX(o.order_date)) > 60 THEN 'dormant'
        WHEN COUNT(o.id) > 5 AND COALESCE(AVG(o.amount), 0) > 100 THEN 'frequent'
        WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - c.signup_date) <= 30 THEN 'new'
        WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - MAX(o.order_date)) > 30 AND COUNT(o.id) > 3 THEN 'at_risk'
        ELSE 'regular'
    END
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.signup_date
ON CONFLICT (customer_id) DO UPDATE SET
    total_orders = EXCLUDED.total_orders,
    total_spend = EXCLUDED.total_spend,
    average_order_value = EXCLUDED.average_order_value,
    last_purchase_date = EXCLUDED.last_purchase_date,
    days_since_last_purchase = EXCLUDED.days_since_last_purchase,
    purchase_frequency = EXCLUDED.purchase_frequency,
    customer_segment = EXCLUDED.customer_segment,
    updated_at = CURRENT_TIMESTAMP;
```

4. Create endpoints:
   - `GET /intelligence/profiles` - Paginated list with filters (segment, min_spend, max_days_inactive)
   - `GET /intelligence/profiles/{customer_id}` - Single profile with orders history
   - `GET /intelligence/segments` - Distribution: count per segment (VIP: 100, Dormant: 150, etc.)
   - `GET /intelligence/summary` - Top spenders, revenue totals, average metrics

**Deliverables:**
- [ ] `POST /intelligence/generate-profiles` computes and stores all metrics
- [ ] Segment distribution matches pre-built dataset (VIP:100, Dormant:150, etc.)
- [ ] `GET /intelligence/profiles` returns paginated, filterable results
- [ ] `GET /intelligence/segments` returns segment counts
- [ ] `GET /intelligence/summary` returns business insights

---

Don't Build Conversion Tracking 

Current:
7-day attribution
campaign_conversions
is good architecture.

But it adds a lot of complexity.

For the first deploy:
Sent
Delivered
Opened
Clicked

is enough.

### PHASE 4: AI Campaign Planner
**Goal:** Convert business goals into structured campaign plans using Groq API.

**Agent Instructions:**
1. Create `app/services/groq_service.py`:
```python
from groq import Groq
import json
from tenacity import retry, stop_after_attempt, wait_exponential

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_campaign_plan(self, business_goal: str) -> dict:
        system_prompt = """You are an expert marketing campaign planner. Convert business goals into structured campaign plans.
You MUST respond with valid JSON only. No markdown, no explanations outside JSON.

Available customer profile fields for filtering:
- total_orders (integer)
- total_spend (decimal)
- average_order_value (decimal)
- days_since_last_purchase (integer)
- purchase_frequency (decimal)
- last_purchase_date (date)
- customer_segment (string: vip, dormant, frequent, new, at_risk, regular)

Available channels: whatsapp, sms, email, rcs

Generate a campaign plan with:
1. audience_name: descriptive name for the target segment
2. filters: array of filter objects with field, operator (>, <, >=, <=, =, !=), value
3. channel: one of available channels
4. strategy: brief description of the marketing approach
5. reasoning: why this plan matches the business goal

Respond in this EXACT JSON structure:
{
  "audience_name": "string",
  "filters": [{"field": "string", "operator": ">|<|>=|<=|=|!=", "value": number|string}],
  "channel": "whatsapp|sms|email|rcs",
  "strategy": "string",
  "reasoning": "string"
}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Business Goal: {business_goal}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1000
        )

        result = json.loads(response.choices[0].message.content)
        return result
```

2. Create endpoint `POST /campaigns/plan`:
   - Request body: `{ "business_goal": "Bring back inactive customers" }`
   - Call Groq service with retry logic
   - Validate response against Pydantic schema
   - Return structured plan (do NOT save to DB yet - this is a preview/planning step)

3. Pydantic v2 Schema for AI Output:
```python
from pydantic import BaseModel, Field
from typing import Literal, Union

class Filter(BaseModel):
    field: str = Field(..., description="Customer profile field name")
    operator: Literal[">", "<", ">=", "<=", "=", "!="]
    value: Union[int, float, str] = Field(..., description="Filter value")

class CampaignPlan(BaseModel):
    audience_name: str = Field(..., description="Descriptive audience segment name")
    filters: list[Filter] = Field(..., description="Audience filter criteria")
    channel: Literal["whatsapp", "sms", "email", "rcs"] = Field(..., description="Communication channel")
    strategy: str = Field(..., description="Marketing strategy description")
    reasoning: str = Field(..., description="AI explanation for this plan")
```

**Deliverables:**
- [ ] `POST /campaigns/plan` accepts business goal and returns structured plan
- [ ] AI output validated against Pydantic schema
- [ ] Retry logic handles transient Groq failures
- [ ] Example: "Bring back inactive customers" returns filters like `days_since_last_purchase > 60`

---

### PHASE 5: Dynamic Audience Builder
**Goal:** Convert AI-generated filters into real audience segments.

**Agent Instructions:**
1. Create `app/services/audience_service.py`:
```python
from sqlalchemy import select, and_
from app.models import CustomerProfile, Customer

class AudienceService:
    def build_query(self, filters: list[Filter]):
        query = select(Customer).join(CustomerProfile).where(CustomerProfile.customer_id == Customer.id)

        conditions = []
        for f in filters:
            field = getattr(CustomerProfile, f.field, None) or getattr(Customer, f.field, None)
            if field is None:
                raise ValueError(f"Invalid filter field: {f.field}")

            if f.operator == ">": conditions.append(field > f.value)
            elif f.operator == "<": conditions.append(field < f.value)
            elif f.operator == ">=": conditions.append(field >= f.value)
            elif f.operator == "<=": conditions.append(field <= f.value)
            elif f.operator == "=": conditions.append(field == f.value)
            elif f.operator == "!=": conditions.append(field != f.value)
            else: raise ValueError(f"Invalid operator: {f.operator}")

        if conditions:
            query = query.where(and_(*conditions))
        return query
```

2. Create endpoints in `app/routers/audience.py`:
   - `POST /audience/preview`:
     - Request: `{ "filters": [{"field": "days_since_last_purchase", "operator": ">", "value": 60}] }`
     - Returns: `{ "audience_size": 150, "sample": [...10 customers...] }`
   - `POST /audience/build`:
     - Request: `{ "campaign_id": 1, "filters": [...] }`
     - Executes query, inserts matching `customer_id`s into `campaign_audience`
     - Updates `campaigns.audience_size`
     - Returns: `{ "audience_size": 150, "campaign_id": 1 }`

3. Create `GET /audience/campaign/{campaign_id}`:
   - Returns full audience list with customer details (paginated)

**Deliverables:**
- [ ] Generic filter engine supports all customer_profile and customer fields
- [ ] `POST /audience/preview` returns accurate size + sample
- [ ] `POST /audience/build` stores audience and updates campaign
- [ ] `GET /audience/campaign/{id}` returns paginated audience details

---

### PHASE 6: Campaign Generator & Approval
**Goal:** Generate personalized campaigns with full lifecycle management.

**Agent Instructions:**
1. Extend `app/routers/campaigns.py`

2. Endpoints:
   - `POST /campaigns` - Save AI plan as draft campaign:
     ```json
     {
       "name": "Dormant Revival Q1",
       "business_goal": "Bring back inactive customers",
       "audience_name": "Dormant Customers",
       "filters": [...],
       "channel": "email",
       "strategy": "15% discount offer",
       "ai_reasoning": "..."
     }
     ```
     - Saves with status = "draft"
     - Triggers audience build automatically

   - `POST /campaigns/{id}/generate-message` - AI generates personalized message:
     - Prompt template:
     ```
     Generate a personalized marketing message for:
     - Channel: {channel}
     - Strategy: {strategy}
     - Target Audience: {audience_name}

     Requirements:
     - Use placeholder {name} for customer name
     - Use placeholder {days_since_last_purchase} for inactivity reference
     - Use placeholder {city} for geographic personalization
     - Include the offer/strategy clearly
     - Add a clear call-to-action
     - Tone should match the channel (professional for email, concise for SMS)

     Return JSON: {"message": "string", "subject": "string (for email only)"}
     ```
     - Updates campaign.message_template and status = "ready"

   - `POST /campaigns/{id}/approve` - Changes status "ready" -> "approved"
     - Validates campaign has audience_size > 0, message_template, and channel

   - `GET /campaigns` - List all campaigns with status filter and pagination
   - `GET /campaigns/{id}` - Full campaign details including audience, message, status history

3. Status Lifecycle Enforcement:
```
draft -> ready -> approved -> running -> completed
              -> failed
```
   - Only valid transitions allowed
   - Return 400 with clear error for invalid transitions

**Deliverables:**
- [ ] Campaign CRUD with proper status management
- [ ] AI message generation with personalization tokens
- [ ] Approval workflow with validation
- [ ] Campaign list with filtering by status
- [ ] Status transition validation

---

### PHASE 7: Campaign Execution Engine
**Goal:** Launch approved campaigns and dispatch personalized messages.

**Agent Instructions:**
1. Create `app/services/executor_service.py`

2. Create endpoint `POST /campaigns/{id}/launch`:
   - Validates campaign status = "approved"
   - Changes status to "running"
   - Triggers BackgroundTasks for async execution

3. Execution Flow (BackgroundTasks):
```python
async def execute_campaign(campaign_id: int, db: AsyncSession):
    campaign = await get_campaign(campaign_id, db)
    audience = await get_campaign_audience(campaign_id, db)

    for customer in audience:  #instead  Use asyncio.gather()
        # Personalize message
        personalized = campaign.message_template
        personalized = personalized.replace("{name}", customer.name or "Valued Customer")
        personalized = personalized.replace("{days_since_last_purchase}", str(customer.profile.days_since_last_purchase) if customer.profile else "a while")
        personalized = personalized.replace("{city}", customer.city or "your city")

        # Send to channel service
        response = await channel_client.send_message(
            campaign_id=campaign_id,
            customer_id=customer.id,
            channel=campaign.channel,
            message=personalized,
            phone=customer.phone,
            email=customer.email,
            subject=campaign.subject_line
        )

        # Log communication
        await log_communication(
            campaign_id=campaign_id,
            customer_id=customer.id,
            channel=campaign.channel,
            message=campaign.message_template,
            personalized_message=personalized,
            status="sent",
            metadata={"channel_message_id": response.get("message_id")}
        )

    # Update campaign status
    await update_campaign_status(campaign_id, "completed", db)
```

4. Create `app/services/channel_client.py`:
```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class ChannelClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def send_message(self, campaign_id, customer_id, channel, message, phone=None, email=None, subject=None):
        payload = {
            "campaign_id": campaign_id,
            "customer_id": customer_id,
            "channel": channel,
            "message": message,
            "phone": phone,
            "email": email,
            "subject": subject
        }
        response = await self.client.post(f"{self.base_url}/send", json=payload)
        response.raise_for_status()
        return response.json()
```

5. Error Handling:
   - If >50% messages fail, mark campaign as "failed"
   - Store error details in `communication_logs.error_message`
   - Continue processing remaining customers even if some fail

**Deliverables:**
- [ ] `POST /campaigns/{id}/launch` triggers async execution
- [ ] Messages personalized with customer data (name, days_since_last_purchase, city)
- [ ] All communications logged with personalized_message stored
- [ ] Campaign status updates: running -> completed/failed
- [ ] Channel service integration with retries

---

### PHASE 8: Channel Service
**Goal:** Simulate WhatsApp/SMS/Email/RCS with realistic state machine.

**Agent Instructions:**
1. Create SEPARATE project structure:
```
channel-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── models.py            # SQLAlchemy models (shared DB or SQLite)
│   └── routers/
│       └── messages.py      # Message handling endpoints
├── requirements.txt
└── .env.example
```

2. Database: Use shared PostgreSQL (same Supabase instance) so main backend can read statuses directly from `communication_logs` table.

3. Endpoints:
   - `POST /send`:
     - Request: `{ "campaign_id", "customer_id", "channel", "message", "phone", "email", "subject" }`
     - Response: `{ "message_id": 123, "status": "sent", "timestamp": "..." }`
     - Immediately inserts into `communication_logs` with status="sent"
     - Schedules background task for lifecycle simulation

4. State Machine Simulation (BackgroundTasks):
```python
async def simulate_message_lifecycle(log_id: int):
    import asyncio, random
    from datetime import datetime

    # Delivery delay: 1-5 seconds
    await asyncio.sleep(random.uniform(1, 5))

    # 10% chance of failure at delivery
    if random.random() < 0.1:
        await update_log_status(log_id, "failed", failed_at=datetime.utcnow(), error_message="Delivery failed")
        await notify_backend(log_id, "failed")
        return

    await update_log_status(log_id, "delivered", delivered_at=datetime.utcnow())
    await notify_backend(log_id, "delivered")

    # Open delay: 5-30 seconds, 70% open rate
    await asyncio.sleep(random.uniform(5, 30))
    if random.random() > 0.3:  # 70% open
        await update_log_status(log_id, "opened", opened_at=datetime.utcnow())
        await notify_backend(log_id, "opened")

        # Click delay: 1-10 seconds, 50% of opened click
        await asyncio.sleep(random.uniform(1, 10))
        if random.random() > 0.5:
            await update_log_status(log_id, "clicked", clicked_at=datetime.utcnow())
            await notify_backend(log_id, "clicked")
```

5. Callback to Main Backend:
   - `POST {MAIN_BACKEND_URL}/webhook/callback`
   - Payload:
   ```json
   {
     "campaign_id": 1,
     "customer_id": 10,
     "communication_log_id": 123,
     "event": "opened",
     "timestamp": "2024-01-15T10:30:00Z"
   }
   ```

6. Endpoint `GET /messages/{message_id}/status`:
   - Returns current status and full timeline

**Deliverables:**
- [ ] Channel service running independently on separate port/service
- [ ] `POST /send` accepts messages and returns message_id
- [ ] Realistic state machine: sent -> delivered -> opened -> clicked (with configurable probabilities)
- [ ] 10% failure rate simulation
- [ ] Callbacks sent to main backend for ALL state changes
- [ ] `GET /messages/{id}/status` returns current state

---

### PHASE 9: Analytics & Conversion Tracking
**Goal:** Measure campaign success with real-time metrics and conversion attribution.

**Agent Instructions:**
1. Create `app/routers/analytics.py`

2. Create endpoint `POST /webhook/callback`:
   - Receives callbacks from channel service
   - Updates `communication_logs` status and timestamps based on event type
   - If event = "clicked", trigger conversion tracking background task

3. Conversion Tracking Logic (7-day attribution window):
```python
async def track_conversions(campaign_id: int, customer_id: int, clicked_at: datetime, db: AsyncSession):
    from datetime import timedelta

    seven_days_later = clicked_at + timedelta(days=7)

    result = await db.execute(
        select(Order).where(
            Order.customer_id == customer_id,
            Order.order_date >= clicked_at,
            Order.order_date <= seven_days_later
        )
    )
    orders = result.scalars().all()

    for order in orders:
        # Check if not already converted
        existing = await db.execute(
            select(CampaignConversion).where(
                CampaignConversion.campaign_id == campaign_id,
                CampaignConversion.customer_id == customer_id,
                CampaignConversion.order_id == order.id
            )
        )
        if not existing.scalar_one_or_none():
            conversion = CampaignConversion(
                campaign_id=campaign_id,
                customer_id=customer_id,
                order_id=order.id,
                conversion_value=order.amount,
                attribution_window_days=7
            )
            db.add(conversion)

    await db.commit()
```

4. Create endpoint `GET /analytics/campaigns/{campaign_id}`:
```json
{
  "campaign_id": 1,
  "name": "Dormant Customers Revival",
  "status": "completed",
  "audience_size": 500,
  "channel": "email",
  "metrics": {
    "sent": 500,
    "delivered": 480,
    "opened": 336,
    "clicked": 168,
    "failed": 20,
    "converted": 25,
    "conversion_rate": "14.88%",
    "revenue_generated": 12500.00,
    "average_order_value": 500.00
  },
  "funnel": {
    "sent_to_delivered": "96.0%",
    "delivered_to_opened": "70.0%",
    "opened_to_clicked": "50.0%",
    "clicked_to_converted": "14.88%",
    "overall_conversion": "5.0%"
  },
  "timeline": [
    {"hour": 0, "sent": 500, "delivered": 0, "opened": 0, "clicked": 0},
    {"hour": 1, "sent": 0, "delivered": 480, "opened": 50, "clicked": 10},
    ...
  ]
}
```

5. Create endpoint `GET /analytics/dashboard`:
   - Aggregate across all campaigns:
   ```json
   {
     "total_customers": 1000,
     "total_orders": 10500,
     "total_revenue": 450000.00,
     "total_campaigns": 15,
     "active_campaigns": 3,
     "overall_metrics": {
       "total_sent": 7500,
       "total_delivered": 7200,
       "total_opened": 5040,
       "total_clicked": 2520,
       "total_converted": 375,
       "total_revenue_from_campaigns": 85000.00
     },
     "top_campaigns": [...],
     "segment_performance": {
       "vip": {"sent": 100, "converted": 20, "rate": "20%"},
       "dormant": {"sent": 150, "converted": 15, "rate": "10%"},
       ...
     }
   }
   ```

6. Create endpoint `GET /analytics/campaigns/{id}/timeline`:
   - Time-series data grouped by hour for Recharts
   - Fields: hour, sent, delivered, opened, clicked, converted

**Deliverables:**
- [ ] Webhook receives and processes channel callbacks
- [ ] 7-day conversion attribution window working
- [ ] Campaign metrics calculated accurately from communication_logs
- [ ] Dashboard aggregates across all campaigns
- [ ] Timeline endpoint returns chart-ready time-series data
- [ ] Segment performance breakdown

---

### PHASE 10: Frontend UI
**Goal:** Build the complete user interface consuming all backend APIs.

**Agent Instructions:**
1. Create Next.js 14+ project with App Router:
```
frontend/
├── app/
│   ├── layout.tsx                    # Root layout with providers
│   ├── page.tsx                      # Dashboard (home)
│   ├── upload/
│   │   └── page.tsx                 # Data Upload
│   ├── planner/
│   │   └── page.tsx                 # AI Campaign Planner
│   ├── campaigns/
│   │   ├── page.tsx                 # Campaign List
│   │   └── [id]/
│   │       └── page.tsx             # Campaign Detail
│   ├── analytics/
│   │   └── page.tsx                 # Analytics Dashboard
│   └── globals.css
├── components/
│   ├── ui/                          # ShadCN components (auto-installed)
│   ├── dashboard/
│   │   ├── StatsCards.tsx           # KPI cards (customers, orders, campaigns, revenue)
│   │   ├── CampaignSummary.tsx      # Recent campaigns table
│   │   └── QuickActions.tsx         # Upload / Create Campaign buttons
│   ├── upload/
│   │   ├── CSVUploader.tsx          # Drag-drop upload with progress
│   │   └── DataQualityReport.tsx    # Error table with row details
│   ├── planner/
│   │   ├── GoalInput.tsx            # Business goal text area
│   │   ├── CampaignPlanCard.tsx     # AI plan display (audience, filters, channel, strategy)
│   │   ├── AudiencePreview.tsx      # Size + sample table
│   │   └── CreateCampaignButton.tsx # Save plan as draft
│   ├── campaigns/
│   │   ├── CampaignList.tsx         # Table with sorting/filtering
│   │   ├── CampaignStatusBadge.tsx  # Color-coded status badges
│   │   ├── CampaignActions.tsx      # Approve / Launch / View buttons
│   │   └── CampaignMessagePreview.tsx # Message with highlighted tokens
│   └── analytics/
│       ├── FunnelChart.tsx          # Recharts BarChart (sent->delivered->opened->clicked->converted)
│       ├── MetricsCards.tsx         # Sent, Opened, Clicked, Converted, Revenue
│       ├── ConversionChart.tsx      # Recharts AreaChart (timeline)
│       ├── SegmentBreakdown.tsx     # PieChart by customer segment
│       └── CampaignSelector.tsx     # Dropdown to select campaign
├── lib/
│   ├── api.ts                       # Axios instance + all API calls
│   └── utils.ts                     # cn() helper, formatters
├── types/
│   └── index.ts                     # TypeScript interfaces matching Pydantic schemas
└── next.config.js
```

2. API Client (`lib/api.ts`):
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: { 'Content-Type': 'application/json' }
});

// Upload
export const uploadCustomers = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload/customers', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
};
export const uploadOrders = (file: File) => { /* same pattern */ };

// Intelligence
export const generateProfiles = () => api.post('/intelligence/generate-profiles');
export const getProfiles = (params?: { segment?: string; page?: number }) => api.get('/intelligence/profiles', { params });
export const getSegments = () => api.get('/intelligence/segments');
export const getSummary = () => api.get('/intelligence/summary');

// Campaigns
export const generatePlan = (goal: string) => api.post('/campaigns/plan', { business_goal: goal });
export const createCampaign = (data: CampaignPlan) => api.post('/campaigns', data);
export const generateMessage = (id: number) => api.post(`/campaigns/${id}/generate-message`);
export const approveCampaign = (id: number) => api.post(`/campaigns/${id}/approve`);
export const launchCampaign = (id: number) => api.post(`/campaigns/${id}/launch`);
export const getCampaigns = (status?: string) => api.get('/campaigns', { params: { status } });
export const getCampaign = (id: number) => api.get(`/campaigns/${id}`);

// Audience
export const previewAudience = (filters: Filter[]) => api.post('/audience/preview', { filters });
export const buildAudience = (campaignId: number, filters: Filter[]) => api.post('/audience/build', { campaign_id: campaignId, filters });

// Analytics
export const getCampaignAnalytics = (id: number) => api.get(`/analytics/campaigns/${id}`);
export const getDashboardStats = () => api.get('/analytics/dashboard');
export const getTimeline = (id: number) => api.get(`/analytics/campaigns/${id}/timeline`);
```

3. Pages to Implement:

   **Dashboard (`/`)**:
   - Stats cards: Total Customers (1000), Total Orders (~10500), Active Campaigns, Total Revenue, Conversion Rate
   - Recent campaigns table (last 5)
   - Quick actions: "Upload Data", "Create Campaign" buttons
   - Segment distribution chart (PieChart)

   **Data Upload (`/upload`)**:
   - Two drag-and-drop zones: Customers CSV, Orders CSV
   - Upload progress indicator
   - Data quality report display (errors table with row numbers)
   - Success toast on completion
   - "Generate Profiles" button after both uploads complete

   **AI Planner (`/planner`)**:
   - Text area for business goal input
   - "Generate Plan" button with loading skeleton
   - Display AI-generated plan card:
     - Audience name + description
     - Filter badges (e.g., "days_since_last_purchase > 60")
     - Channel badge (whatsapp/sms/email/rcs)
     - Strategy text
     - AI reasoning (collapsible)
   - Audience preview section: size count + sample table (10 rows)
   - "Create Campaign" button -> saves as draft -> redirects to campaign detail

   **Campaigns (`/campaigns`)**:
   - Table with columns: Name, Status, Audience Size, Channel, Created Date, Actions
   - Status badges with colors:
     - draft = gray
     - ready = blue
     - approved = purple
     - running = amber (animated pulse)
     - completed = green
     - failed = red
   - Filter by status tabs
   - Actions per row:
     - draft: View, Edit, Delete
     - ready: View, Approve
     - approved: View, Launch
     - running: View (disabled actions)
     - completed: View Analytics
     - failed: View, Retry

   **Campaign Detail (`/campaigns/[id]`)**:
   - Campaign info card: name, status badge, channel, audience size
   - Message preview card with highlighted tokens {name}, {days_since_last_purchase}, {city}
   - Audience list table (paginated, 50 per page)
   - Action buttons based on status:
     - If draft: Generate Message
     - If ready: Approve
     - If approved: Launch
     - If completed: View Analytics
   - Activity log (status changes)

   **Analytics (`/analytics`)**:
   - Campaign selector dropdown (all completed campaigns)
   - Metrics cards row: Sent, Delivered, Opened, Clicked, Converted, Revenue
   - Funnel chart (Recharts BarChart): visual funnel from sent to converted
   - Conversion timeline (Recharts AreaChart): events over time
   - Segment performance table: conversion rate by customer segment
   - Top customers table: highest conversion value

4. ShadCN Components to Install:
```bash
npx shadcn@latest add button card input textarea table badge dialog tabs select toast skeleton sheet dropdown-menu separator avatar progress
```

5. Charts (Recharts):
   - `FunnelChart`: BarChart with gradient colors showing drop-off at each stage
   - `ConversionChart`: AreaChart with sent/delivered/opened/clicked/converted lines over time
   - `SegmentPie`: PieChart showing campaign performance by customer segment
   - `DashboardStats`: Simple bar chart for top campaigns

6. Styling:
   - Tailwind CSS with custom color scheme (slate/blue primary, emerald for success, rose for failure)
   - Responsive design (mobile-first, sidebar collapses on mobile)
   - Loading states with ShadCN Skeleton components
   - Toast notifications for all actions (success/error)
   - Dark mode support via next-themes

**Deliverables:**
- [ ] All 6 pages implemented and functional
- [ ] API integration working with all backend endpoints
- [ ] Charts rendering with Recharts (funnel, timeline, segment breakdown)
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Loading skeletons and error states
- [ ] Toast notifications for user feedback
- [ ] Deployed on Vercel

---

## 6. DEPLOYMENT CONFIGURATION

### 6.1 Environment Variables

**Backend (.env)**:
```
DATABASE_URL=postgresql+asyncpg://user:pass@db.supabase.co:5432/postgres
GROQ_API_KEY=gsk_xxxxxxxx
CHANNEL_SERVICE_URL=https://channel-service.onrender.com
ENVIRONMENT=production
```

**Channel Service (.env)**:
```
DATABASE_URL=postgresql+asyncpg://user:pass@db.supabase.co:5432/postgres
MAIN_BACKEND_URL=https://backend.onrender.com
ENVIRONMENT=production
```

**Frontend (.env.local)**:
```
NEXT_PUBLIC_API_URL=https://backend.onrender.com
```

### 6.2 Deployment Commands

**Backend (Render):**
```bash
# Build command
pip install -r requirements.txt

# Start command
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Channel Service (Render):**
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Frontend (Vercel):**
```bash
# Build settings
Framework: Next.js
Build Command: next build
Output Directory: .next
```

### 6.3 CORS Configuration
Backend must allow:
- Frontend Vercel domain: `https://xeno-frontend.vercel.app`
- Channel Service Render domain: `https://xeno-channel.onrender.com`

---

## 7. TESTING CHECKLIST

### End-to-End Test Flow:
1. [ ] Upload `customers.csv` -> Verify data quality report (1000 customers)
2. [ ] Upload `orders.csv` -> Verify validation (9000-12000 orders)
3. [ ] Generate profiles -> Verify segment distribution matches dataset (VIP:100, Dormant:150, etc.)
4. [ ] Enter business goal "Bring back inactive customers" -> Verify AI plan with `days_since_last_purchase > 60`
5. [ ] Preview audience -> Verify filter engine returns ~150 dormant customers
6. [ ] Create campaign -> Verify DB entry with status "draft"
7. [ ] Generate message -> Verify personalization tokens {name}, {days_since_last_purchase}, {city}
8. [ ] Approve campaign -> Verify status change to "approved"
9. [ ] Launch campaign -> Verify messages dispatched to channel service
10. [ ] Check channel service -> Verify state transitions (sent->delivered->opened->clicked)
11. [ ] Check analytics -> Verify metrics, funnel, and 7-day conversion attribution

---

## 8. AGENT HANDOFF NOTES

### For Each Phase Agent:
1. Read this entire brief first
2. Implement ONLY your assigned phase
3. Ensure all previous phase endpoints still work (run health checks)
4. Write a brief `PHASE_X_SUMMARY.md` documenting:
   - What was built
   - API endpoints created/modified
   - Database changes (migrations)
   - New dependencies added
   - Known issues or TODOs
   - Test results
5. Update `requirements.txt` or `package.json` if new dependencies added

### Dependencies Between Phases:
| Phase | Depends On | Required For |
|-------|-----------|--------------|
| Phase 0 | - | Phase 2, 3 |
| Phase 1 | - | ALL backend phases |
| Phase 2 | Phase 1 | Phase 3 |
| Phase 3 | Phase 2 | Phase 4, 5, 9 |
| Phase 4 | Phase 1 | Phase 5, 6 |
| Phase 5 | Phase 3, 4 | Phase 6 |
| Phase 6 | Phase 5 | Phase 7 |
| Phase 7 | Phase 6, 8 | Phase 9 |
| Phase 8 | Phase 1 | Phase 7, 9 |
| Phase 9 | Phase 7, 8 | Phase 10 |
| Phase 10 | ALL backend | - |

### Recommended Agent Assignment:
| Agent | Phases | Focus | Estimated Effort |
|-------|--------|-------|-----------------|
| Agent 1 | Phase 1 + Phase 8 | Infrastructure setup (Backend + Channel Service skeleton) | Medium |
| Agent 2 | Phase 2 + Phase 3 | Data layer (Upload + Intelligence Engine) | Medium |
| Agent 3 | Phase 4 + Phase 5 + Phase 6 | AI + Campaigns (Planner + Audience + Generator) | High |
| Agent 4 | Phase 7 + Phase 9 | Execution + Analytics (Launch + Tracking) | High |
| Agent 5 | Phase 10 | Frontend UI (All pages + charts) | High |

### Handoff Checklist:
Before passing to next agent:
- [ ] All endpoints tested with curl/Postman
- [ ] Database schema matches Section 4
- [ ] `.env.example` updated with new variables
- [ ] `PHASE_X_SUMMARY.md` written
- [ ] No hardcoded secrets
- [ ] Code committed to git

---

## 9. SAMPLE DATA REFERENCE

### customers.csv (from pre-built dataset)
```csv
customer_id,name,email,phone,city,signup_date
1,John Doe,john@example.com,+1234567890,New York,2023-01-15
2,Jane Smith,jane@example.com,+1987654321,Los Angeles,2023-02-20
3,Bob Johnson,bob@example.com,+1122334455,Chicago,2023-03-10
...
# 1000 total rows with intentional business segments
```

### orders.csv (from pre-built dataset)
```csv
order_id,customer_id,amount,order_date,category
1,1,150.00,2024-01-15 10:30:00,Electronics
2,1,230.50,2024-02-20 14:15:00,Clothing
3,2,89.99,2024-03-10 09:00:00,Home
4,3,450.00,2024-01-05 16:45:00,Electronics
...
# 9000-12000 total rows with realistic patterns per segment
```

### customer_profiles.csv (prototype for DB table)
```csv
customer_id,total_orders,total_spend,average_order_value,last_purchase_date,days_since_last_purchase,purchase_frequency
1,15,5230.50,348.70,2024-05-15,27,2.5
2,3,450.00,150.00,2024-01-20,122,0.3
3,8,1890.00,236.25,2024-04-01,71,0.8
...
```

---

## 10. ADDITIONAL NOTES

### Performance Considerations:
- Use database connection pooling (pool_size=5, max_overflow=10)
- Process campaign execution in batches of 100 customers
- Add pagination to ALL list endpoints (default 50, max 500)
- Use database indexes on frequently queried fields (see Section 4)
- Cache AI-generated plans for identical business goals (Redis optional)

### Security Considerations:
- Validate all CSV uploads (file size limit: 10MB)
- Sanitize AI-generated messages before sending
- Rate limit API endpoints (optional: slowapi)
- Use HTTPS everywhere in production
- Store API keys in environment variables only

### Error Handling Patterns:
```python
# Backend pattern
try:
    result = await some_operation()
    return {"success": True, "data": result, "message": "Operation successful"}
except ValueError as e:
    return {"success": False, "data": None, "message": str(e)}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"success": False, "data": None, "message": "Internal server error"}
```

```typescript
// Frontend pattern
try {
  const response = await api.post('/campaigns/plan', { business_goal });
  setPlan(response.data.data);
  toast.success('Campaign plan generated!');
} catch (error: any) {
  toast.error(error.response?.data?.message || 'Failed to generate plan');
}
```

---

**END OF IMPLEMENTATION BRIEF v2.0**
