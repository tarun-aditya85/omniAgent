# OmniGrowth OS - Enterprise SaaS Platform Implementation Plan

## Context

Building **OmniGrowth OS** - a unified AI Operating System for Media Agencies and Brand Growth Teams. This replaces fragmented tooling (DSPs, ad managers, analytics, SEO tools, influencer platforms, reporting tools) with a single platform featuring:

- **Multi-tenant architecture** supporting agencies → clients → ad accounts hierarchy
- **Unified integrations** across Google Ads, Meta, DV360, Trade Desk, LinkedIn, TikTok, Amazon Ads
- **ML-powered optimization engine** for CPA/CPC/ROAS optimization with automated recommendations
- **Intelligence layers**: Brand health, competitor tracking, influencer CRM, SEO/AEO optimization
- **AI Copilot** with RAG over metrics for strategic insights
- **White-label reporting engine** for client exports

**Not a toy dashboard** - this is "Bloomberg Terminal + HubSpot + Trade Desk + SEMrush + AI Copilot for Agencies"

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │  Campaigns   │  │  AI Copilot  │      │
│  │  (Command    │  │  (Editable   │  │  (Chat RAG)  │      │
│  │   Center)    │  │    Grid)     │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │  API Gateway  │
                    │   (FastAPI)   │
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼─────────┐
│  Campaign Svc  │  │  ML Svc     │  │  Intelligence Svc │
│  - CRUD        │  │  - Optimize │  │  - Brand/Comp     │
│  - Connectors  │  │  - Predict  │  │  - SEO/AEO        │
└────────┬───────┘  └──────┬──────┘  └────────┬──────────┘
         │                 │                   │
         └────────┬────────┴─────────┬─────────┘
                  │                  │
         ┌────────▼────────┐  ┌─────▼──────┐
         │  PostgreSQL     │  │  ClickHouse │
         │  (Transactional)│  │  (Analytics)│
         └─────────────────┘  └────────────┘
                  │
         ┌────────▼────────┐
         │  Redis/Valkey   │
         │  (Cache/Queue)  │
         └─────────────────┘
```

### Tech Stack

**Frontend:**
- Next.js 14+ (App Router)
- React 18 + TypeScript
- TailwindCSS + shadcn/ui
- Recharts for visualizations
- Zustand for state management

**Backend:**
- FastAPI (Python 3.11+)
- Pydantic v2 for schemas
- SQLAlchemy 2.0 (async)
- Alembic for migrations

**Workers:**
- Celery with Redis broker
- Dramatiq (alternative)

**Databases:**
- PostgreSQL 15+ (primary, with RLS for multi-tenancy)
- ClickHouse (optional analytics DB)
- Redis 7+ (cache, queues, sessions)

**ML/AI:**
- scikit-learn, XGBoost, LightGBM
- PyTorch (optional for deep learning)
- LangChain + OpenAI/Claude for AI Copilot RAG

**Auth & Security:**
- JWT tokens with refresh mechanism
- RBAC (5 roles: Super Admin, Agency Admin, Trader, Analyst, Client Viewer)
- Row-Level Security (RLS) for tenant isolation

**Infrastructure:**
- Docker + Docker Compose
- Kubernetes-ready (Helm charts)
- GitHub Actions for CI/CD
- OpenTelemetry for observability

---

## Database Schema

### Core Tables

```sql
-- Tenant hierarchy
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'agency' | 'brand'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    settings JSONB
);

CREATE TABLE clients (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users & Auth
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL, -- 'super_admin' | 'agency_admin' | 'trader' | 'analyst' | 'viewer'
    organization_id UUID REFERENCES organizations(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_client_access (
    user_id UUID REFERENCES users(id),
    client_id UUID REFERENCES clients(id),
    PRIMARY KEY (user_id, client_id)
);

-- Platform Connections
CREATE TABLE platform_connections (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    platform VARCHAR(50) NOT NULL, -- 'google_ads' | 'meta' | 'dv360' | 'ttd' | 'linkedin' | 'tiktok' | 'amazon'
    account_id VARCHAR(255) NOT NULL,
    credentials_encrypted TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    last_sync_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(client_id, platform, account_id)
);

-- Campaigns
CREATE TABLE campaigns (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    platform_connection_id UUID REFERENCES platform_connections(id),
    external_id VARCHAR(255), -- ID from DSP
    name VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- 'active' | 'paused' | 'ended'
    objective VARCHAR(100), -- 'conversions' | 'traffic' | 'awareness'
    budget_daily DECIMAL(12,2),
    budget_total DECIMAL(12,2),
    start_date DATE,
    end_date DATE,
    target_cpa DECIMAL(10,2),
    target_roas DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_campaigns_client ON campaigns(client_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);

-- Ad Groups
CREATE TABLE ad_groups (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    external_id VARCHAR(255),
    name VARCHAR(500),
    bid_amount DECIMAL(10,2),
    status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Creatives
CREATE TABLE creatives (
    id UUID PRIMARY KEY,
    ad_group_id UUID REFERENCES ad_groups(id),
    external_id VARCHAR(255),
    type VARCHAR(50), -- 'image' | 'video' | 'carousel' | 'text'
    headline TEXT,
    description TEXT,
    media_url TEXT,
    ctr DECIMAL(5,4),
    status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Metrics (Time-series)
CREATE TABLE daily_metrics (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    date DATE NOT NULL,
    spend DECIMAL(12,2) DEFAULT 0,
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    conversions BIGINT DEFAULT 0,
    installs BIGINT DEFAULT 0,
    revenue DECIMAL(12,2) DEFAULT 0,
    cpa DECIMAL(10,2),
    cpc DECIMAL(10,2),
    cpi DECIMAL(10,2),
    roas DECIMAL(10,2),
    ctr DECIMAL(5,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(campaign_id, date)
);

CREATE INDEX idx_daily_metrics_campaign_date ON daily_metrics(campaign_id, date DESC);

CREATE TABLE hourly_metrics (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    hour TIMESTAMPTZ NOT NULL,
    spend DECIMAL(12,2),
    impressions BIGINT,
    clicks BIGINT,
    conversions BIGINT,
    UNIQUE(campaign_id, hour)
);

-- ML Recommendations
CREATE TABLE recommendations (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    action_type VARCHAR(100) NOT NULL, -- 'increase_budget' | 'decrease_budget' | 'pause_campaign' | 'raise_bid' | 'lower_bid' | 'rotate_creative'
    reason TEXT NOT NULL,
    confidence DECIMAL(5,4), -- 0.0 to 1.0
    estimated_impact JSONB, -- {"savings": 42000, "conversions_gain": 120}
    status VARCHAR(50) DEFAULT 'pending', -- 'pending' | 'applied' | 'dismissed'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_recommendations_campaign ON recommendations(campaign_id);
CREATE INDEX idx_recommendations_status ON recommendations(status);

-- Alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    campaign_id UUID REFERENCES campaigns(id),
    severity VARCHAR(50), -- 'critical' | 'warning' | 'info'
    type VARCHAR(100), -- 'budget_pacing' | 'cpa_spike' | 'creative_fatigue' | 'low_quality_score'
    message TEXT NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Competitor Intelligence
CREATE TABLE competitors (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE competitor_metrics (
    id UUID PRIMARY KEY,
    competitor_id UUID REFERENCES competitors(id),
    date DATE NOT NULL,
    estimated_traffic BIGINT,
    paid_intensity_score DECIMAL(5,2),
    seo_overlap_score DECIMAL(5,2),
    keyword_overlap JSONB,
    UNIQUE(competitor_id, date)
);

-- Influencer Marketing
CREATE TABLE influencers (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50), -- 'instagram' | 'youtube' | 'tiktok'
    handle VARCHAR(255),
    followers BIGINT,
    engagement_rate DECIMAL(5,4),
    niche VARCHAR(100),
    cost_per_post DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE influencer_campaigns (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    influencer_id UUID REFERENCES influencers(id),
    campaign_name VARCHAR(500),
    promo_code VARCHAR(50),
    start_date DATE,
    end_date DATE,
    cost DECIMAL(10,2),
    conversions BIGINT,
    revenue DECIMAL(12,2),
    roi DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SEO
CREATE TABLE seo_keywords (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    keyword TEXT NOT NULL,
    search_volume BIGINT,
    difficulty_score DECIMAL(5,2),
    current_rank INT,
    target_rank INT,
    url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AEO (Answer Engine Optimization)
CREATE TABLE aeo_entities (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    entity_name VARCHAR(255),
    entity_type VARCHAR(100), -- 'brand' | 'product' | 'person'
    citation_score DECIMAL(5,2), -- 0-100
    mention_score DECIMAL(5,2),
    faq_coverage DECIMAL(5,2),
    schema_completeness DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Reports
CREATE TABLE reports (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    created_by UUID REFERENCES users(id),
    report_type VARCHAR(50), -- 'monthly' | 'weekly' | 'custom'
    date_from DATE,
    date_to DATE,
    file_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id),
    action VARCHAR(100), -- 'campaign.created' | 'budget.updated' | 'report.exported'
    resource_type VARCHAR(100),
    resource_id UUID,
    changes JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_org ON audit_logs(organization_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
```

---

## Project Structure

```
omnigrowth-os/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Settings (Pydantic BaseSettings)
│   │   ├── dependencies.py            # DI containers (DB session, auth)
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py            # JWT, password hashing
│   │   │   ├── tenant.py              # TenantContext middleware
│   │   │   ├── rbac.py                # Role-based access control
│   │   │   └── exceptions.py          # Custom exceptions
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # SQLAlchemy Base
│   │   │   ├── session.py             # Async session factory
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       ├── user.py
│   │   │       ├── organization.py
│   │   │       ├── client.py
│   │   │       ├── campaign.py
│   │   │       ├── metric.py
│   │   │       ├── recommendation.py
│   │   │       ├── competitor.py
│   │   │       ├── influencer.py
│   │   │       ├── seo.py
│   │   │       └── aeo.py
│   │   │
│   │   ├── schemas/                   # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── campaign.py
│   │   │   ├── metric.py
│   │   │   ├── recommendation.py
│   │   │   ├── influencer.py
│   │   │   └── report.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py          # Aggregate all routers
│   │   │       ├── auth.py            # /auth/login, /auth/register
│   │   │       ├── clients.py         # /clients
│   │   │       ├── campaigns.py       # /campaigns CRUD
│   │   │       ├── integrations.py    # /integrations/connect, /integrations/sync
│   │   │       ├── metrics.py         # /metrics/overview, /metrics/campaigns/{id}
│   │   │       ├── recommendations.py # /recommendations
│   │   │       ├── optimizer.py       # /optimizer/run
│   │   │       ├── seo.py             # /seo/audit, /seo/keywords
│   │   │       ├── aeo.py             # /aeo/audit
│   │   │       ├── influencers.py     # /influencers
│   │   │       ├── competitors.py     # /competitors
│   │   │       ├── reports.py         # /reports/export
│   │   │       └── copilot.py         # /copilot/chat (AI assistant)
│   │   │
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── campaign_service.py
│   │   │   ├── integration_service.py
│   │   │   ├── metric_service.py
│   │   │   ├── recommendation_service.py
│   │   │   ├── influencer_service.py
│   │   │   ├── seo_service.py
│   │   │   ├── aeo_service.py
│   │   │   └── report_service.py
│   │   │
│   │   ├── repositories/              # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Generic CRUD repository
│   │   │   ├── campaign_repo.py
│   │   │   ├── metric_repo.py
│   │   │   ├── recommendation_repo.py
│   │   │   └── client_repo.py
│   │   │
│   │   ├── connectors/                # Ad platform integrations
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # AbstractDSPAdapter
│   │   │   ├── normalizer.py          # Unified campaign/metric models
│   │   │   ├── google_ads/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── adapter.py
│   │   │   │   └── client.py
│   │   │   ├── meta/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── adapter.py
│   │   │   │   └── client.py
│   │   │   ├── dv360/
│   │   │   ├── trade_desk/
│   │   │   ├── linkedin/
│   │   │   ├── tiktok/
│   │   │   └── amazon/
│   │   │
│   │   ├── ml/                        # ML optimization engine
│   │   │   ├── __init__.py
│   │   │   ├── optimizer_engine.py    # Main optimization orchestrator
│   │   │   ├── feature_engineering.py # Feature extraction from metrics
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── cpa_predictor.py   # CPA prediction model
│   │   │   │   ├── budget_elasticity.py
│   │   │   │   ├── creative_fatigue.py
│   │   │   │   └── churn_risk.py
│   │   │   ├── recommenders/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── budget_recommender.py
│   │   │   │   ├── bid_recommender.py
│   │   │   │   └── creative_recommender.py
│   │   │   └── training/
│   │   │       ├── __init__.py
│   │   │       └── train_pipeline.py  # Batch training jobs
│   │   │
│   │   ├── workers/                   # Celery tasks
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   ├── sync_campaigns.py      # Periodic DSP sync
│   │   │   ├── run_optimizer.py       # Daily optimization run
│   │   │   └── generate_report.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       ├── encryption.py
│   │       └── metrics.py             # Prometheus metrics
│   │
│   ├── alembic/                       # DB migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_api/
│   │   ├── test_services/
│   │   ├── test_connectors/
│   │   └── test_ml/
│   │
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Landing/login
│   │   ├── globals.css
│   │   │
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   │
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx             # Dashboard sidebar layout
│   │   │   ├── [workspaceId]/         # Workspace context
│   │   │   │   ├── page.tsx           # Agency overview dashboard
│   │   │   │   ├── clients/
│   │   │   │   │   ├── page.tsx       # Clients list
│   │   │   │   │   └── [clientId]/
│   │   │   │   │       └── page.tsx   # Client overview
│   │   │   │   ├── campaigns/
│   │   │   │   │   ├── page.tsx       # Campaign table (editable grid)
│   │   │   │   │   └── [campaignId]/
│   │   │   │   │       └── page.tsx   # Campaign detail
│   │   │   │   ├── integrations/
│   │   │   │   │   └── page.tsx       # Connect platforms
│   │   │   │   ├── optimization/
│   │   │   │   │   └── page.tsx       # Recommendations feed
│   │   │   │   ├── seo/
│   │   │   │   │   └── page.tsx       # SEO dashboard
│   │   │   │   ├── aeo/
│   │   │   │   │   └── page.tsx       # AEO dashboard
│   │   │   │   ├── influencers/
│   │   │   │   │   └── page.tsx       # Influencer CRM
│   │   │   │   ├── competitors/
│   │   │   │   │   └── page.tsx       # Competitor intelligence
│   │   │   │   ├── reports/
│   │   │   │   │   └── page.tsx       # Report export center
│   │   │   │   └── copilot/
│   │   │   │       └── page.tsx       # AI chat assistant
│   │   │   │
│   │   │   └── api/                   # Next.js API routes (optional)
│   │   │       └── auth/
│   │   │           └── [...nextauth]/
│   │   │
│   │   └── error.tsx
│   │
│   ├── components/
│   │   ├── ui/                        # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── table.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── AlertsCenter.tsx
│   │   ├── dashboard/
│   │   │   ├── OverviewCards.tsx
│   │   │   ├── SpendChart.tsx
│   │   │   └── PerformanceTable.tsx
│   │   ├── campaigns/
│   │   │   ├── CampaignGrid.tsx       # Editable AG Grid
│   │   │   ├── CampaignFilters.tsx
│   │   │   └── CampaignDetail.tsx
│   │   ├── recommendations/
│   │   │   ├── RecommendationCard.tsx
│   │   │   └── RecommendationFeed.tsx
│   │   └── copilot/
│   │       ├── ChatInterface.tsx
│   │       └── MessageBubble.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                     # API client (fetch wrapper)
│   │   ├── auth.ts                    # Auth helpers
│   │   ├── utils.ts                   # cn() and utilities
│   │   └── stores/                    # Zustand stores
│   │       ├── authStore.ts
│   │       ├── workspaceStore.ts
│   │       └── campaignStore.ts
│   │
│   ├── types/
│   │   ├── api.ts                     # API response types
│   │   ├── campaign.ts
│   │   ├── metric.ts
│   │   └── recommendation.ts
│   │
│   ├── public/
│   │   └── logo.svg
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── Dockerfile
│
├── docker-compose.yml                 # Local dev environment
├── docker-compose.prod.yml            # Production setup
├── .env.example
├── .gitignore
├── README.md
└── docs/
    ├── API.md                         # OpenAPI docs
    ├── DEPLOYMENT.md
    ├── CONTRIBUTING.md
    └── ARCHITECTURE.md
```

---

## Implementation Phases

### **Phase 1: MVP (Core Platform) - 6-8 weeks**

#### Week 1-2: Foundation & Infrastructure
**Backend:**
- Set up FastAPI project structure
- Implement core database models (users, organizations, clients, campaigns)
- Create Alembic migrations
- Build authentication system (JWT, password hashing)
- Implement RBAC middleware
- Set up tenant context middleware
- Configure PostgreSQL with RLS
- Set up Redis for caching/queues

**Frontend:**
- Initialize Next.js 14 project with App Router
- Configure TailwindCSS + shadcn/ui
- Build authentication pages (login, register)
- Create dashboard layout with sidebar
- Implement auth context and protected routes

**DevOps:**
- Create Docker Compose setup (FastAPI, PostgreSQL, Redis)
- Set up environment variable management
- Configure logging (structured JSON logs)

#### Week 3-4: Integrations & Campaign Management
**Backend:**
- Build connector abstraction layer (`AbstractDSPAdapter`)
- Implement Google Ads connector (OAuth2, campaign fetch, metrics sync)
- Implement Meta Ads connector (similar pattern)
- Create normalizer for unified campaign/metric models
- Build campaign CRUD API endpoints
- Implement metrics ingestion pipeline
- Create Celery task for periodic DSP sync

**Frontend:**
- Build clients list page
- Create campaign table page (editable grid with AG Grid or TanStack Table)
- Implement campaign detail view
- Build integrations page (connect Google Ads/Meta)
- Add filters, sorting, pagination to campaign table

#### Week 5-6: Analytics & Optimization Engine
**Backend:**
- Build metrics aggregation service (daily/hourly rollups)
- Implement ML feature engineering pipeline
- Create simple rule-based optimizer (v1):
  - CPA > target → recommend budget decrease
  - CPA < target + high conversions → recommend budget increase
  - CTR declining for 3+ days → recommend creative rotation
- Build recommendations API
- Create recommendation repository and CRUD

**Frontend:**
- Build agency overview dashboard (KPI cards, charts)
- Create client overview dashboard
- Build recommendations feed page
- Add recommendation action buttons (apply, dismiss)
- Implement real-time alerts center (budget pacing, CPA spikes)

#### Week 7-8: Reporting & Polish
**Backend:**
- Build report generation service (PDF/Excel export)
- Implement audit logging
- Add API rate limiting
- Create health check endpoints
- Write integration tests

**Frontend:**
- Build reports page (date range selector, export)
- Add dark mode toggle
- Implement saved views/filters
- Polish UI/UX (loading states, error handling)
- Responsive design for tablets

**Deliverables:**
- Fully working multi-tenant SaaS
- Google Ads + Meta connectors
- Campaign management UI
- Basic ML optimizer with recommendations
- Client reports export
- Docker Compose for local dev

---

### **Phase 2: Intelligence Layers - 4-6 weeks**

#### Week 9-10: SEO & AEO Modules
**Backend:**
- Build SEO service:
  - Integrate Google Search Console API
  - Keyword opportunity analyzer
  - Ranking tracker
  - Content gap detector
  - Internal linking suggestions
- Build AEO service:
  - Citation likelihood scorer (mock initially)
  - Entity graph completeness checker
  - FAQ coverage analyzer
  - Schema markup validator
  - Prompt cluster opportunity finder

**Frontend:**
- Create SEO dashboard (keyword opportunities, ranking trends)
- Build AEO dashboard (citation scores, optimization suggestions)
- Add technical SEO checklist component

#### Week 11-12: Competitor & Influencer Intelligence
**Backend:**
- Build competitor intelligence service:
  - Traffic estimation (integrate SimilarWeb/SEMrush API or mock)
  - Keyword overlap calculator
  - Paid intensity scorer
  - Creative theme analyzer (placeholder)
- Build influencer CRM:
  - Influencer repository and CRUD
  - Campaign tracking
  - ROI calculator
  - AI ranking system (niche matching)

**Frontend:**
- Create competitor intelligence dashboard
- Build influencer CRM pages (list, detail, campaign tracker)
- Add influencer search and ranking UI
- Build promo code tracking component

#### Week 13-14: Advanced Integrations
**Backend:**
- Add DV360 connector
- Add Trade Desk connector
- Add LinkedIn Ads connector
- Add TikTok Ads connector
- Add Amazon Ads connector
- Implement webhook handlers for real-time sync

**Frontend:**
- Update integrations page with new platforms
- Add platform-specific configuration flows

---

### **Phase 3: AI Automation & Scale - 4-6 weeks**

#### Week 15-16: AI Copilot
**Backend:**
- Build RAG system over metrics data
- Integrate LangChain + OpenAI/Claude API
- Create vector embeddings for campaigns/metrics
- Build chat API endpoint with context injection
- Implement conversation memory

**Frontend:**
- Create AI Copilot chat interface
- Add suggested questions UI
- Build context cards (campaign mentions, metric visualizations)
- Implement streaming responses

#### Week 17-18: Advanced ML Models
**Backend:**
- Train CPA prediction model (XGBoost)
- Build budget elasticity model (multi-armed bandit)
- Create creative fatigue detector (time-series analysis)
- Implement churn risk predictor (client satisfaction)
- Add A/B testing framework for recommendations
- Build automated execution pipeline (optional: auto-apply recommendations)

**Frontend:**
- Add ML model performance dashboard (accuracy, precision, recall)
- Build A/B test results visualization
- Create auto-execution settings page

#### Week 19-20: Scale & Observability
**Backend:**
- Implement ClickHouse for analytics DB (faster metric queries)
- Add OpenTelemetry tracing
- Set up Prometheus metrics
- Integrate Sentry for error tracking
- Build admin panel API (user management, tenant settings)

**Frontend:**
- Create admin panel UI
- Build system health dashboard
- Add feature flags UI
- Implement usage analytics dashboard

---

## Critical Files to Create (Priority Order)

### Backend
1. **`backend/app/main.py`** - FastAPI app with middleware, routers
2. **`backend/app/config.py`** - Settings (DB URL, Redis, secrets)
3. **`backend/app/core/security.py`** - JWT auth, password hashing
4. **`backend/app/core/tenant.py`** - Multi-tenant middleware
5. **`backend/app/db/models/`** - All SQLAlchemy models
6. **`backend/app/api/v1/auth.py`** - Login/register endpoints
7. **`backend/app/api/v1/campaigns.py`** - Campaign CRUD
8. **`backend/app/connectors/base.py`** - AbstractDSPAdapter interface
9. **`backend/app/connectors/google_ads/adapter.py`** - Google Ads implementation
10. **`backend/app/connectors/meta/adapter.py`** - Meta Ads implementation
11. **`backend/app/ml/optimizer_engine.py`** - ML optimization orchestrator
12. **`backend/app/services/recommendation_service.py`** - Recommendation business logic
13. **`backend/alembic/versions/001_initial_schema.py`** - Initial migration

### Frontend
1. **`frontend/app/layout.tsx`** - Root layout with providers
2. **`frontend/app/(auth)/login/page.tsx`** - Login page
3. **`frontend/app/(dashboard)/layout.tsx`** - Dashboard layout with sidebar
4. **`frontend/app/(dashboard)/[workspaceId]/page.tsx`** - Agency overview
5. **`frontend/app/(dashboard)/[workspaceId]/campaigns/page.tsx`** - Campaign table
6. **`frontend/components/campaigns/CampaignGrid.tsx`** - Editable grid
7. **`frontend/components/dashboard/OverviewCards.tsx`** - KPI cards
8. **`frontend/lib/api.ts`** - API client
9. **`frontend/lib/stores/authStore.ts`** - Auth state management

### Infrastructure
1. **`docker-compose.yml`** - Local dev environment
2. **`backend/Dockerfile`** - FastAPI container
3. **`frontend/Dockerfile`** - Next.js container
4. **`.env.example`** - Environment variables template

---

## API Design (Key Endpoints)

### Authentication
```
POST   /api/v1/auth/register       - Create account
POST   /api/v1/auth/login          - Login (returns JWT)
POST   /api/v1/auth/refresh        - Refresh token
GET    /api/v1/auth/me             - Get current user
```

### Clients
```
GET    /api/v1/clients             - List clients (filtered by org/access)
POST   /api/v1/clients             - Create client
GET    /api/v1/clients/{id}        - Get client detail
PATCH  /api/v1/clients/{id}        - Update client
DELETE /api/v1/clients/{id}        - Delete client
```

### Integrations
```
GET    /api/v1/integrations                     - List connected platforms
POST   /api/v1/integrations/connect             - Initiate OAuth flow
POST   /api/v1/integrations/{id}/sync           - Trigger manual sync
DELETE /api/v1/integrations/{id}/disconnect     - Remove connection
```

### Campaigns
```
GET    /api/v1/campaigns                        - List campaigns (with filters)
POST   /api/v1/campaigns                        - Create campaign
GET    /api/v1/campaigns/{id}                   - Get campaign detail
PATCH  /api/v1/campaigns/{id}                   - Update campaign (budget, bid, status)
DELETE /api/v1/campaigns/{id}                   - Delete campaign
POST   /api/v1/campaigns/{id}/pause             - Pause campaign
POST   /api/v1/campaigns/{id}/resume            - Resume campaign
```

### Metrics
```
GET    /api/v1/metrics/overview                 - Agency-level metrics
GET    /api/v1/metrics/clients/{id}             - Client-level metrics
GET    /api/v1/metrics/campaigns/{id}           - Campaign metrics (time-series)
GET    /api/v1/metrics/campaigns/{id}/hourly    - Hourly breakdown
```

### Recommendations
```
GET    /api/v1/recommendations                  - List recommendations (pending/all)
POST   /api/v1/recommendations/{id}/apply       - Apply recommendation
POST   /api/v1/recommendations/{id}/dismiss     - Dismiss recommendation
```

### Optimizer
```
POST   /api/v1/optimizer/run                    - Trigger optimization (async)
GET    /api/v1/optimizer/status/{job_id}        - Check optimization job status
```

### SEO
```
GET    /api/v1/seo/keywords                     - List keywords for client
POST   /api/v1/seo/audit                        - Run SEO audit
GET    /api/v1/seo/opportunities                - Get keyword opportunities
```

### AEO
```
POST   /api/v1/aeo/audit                        - Run AEO audit
GET    /api/v1/aeo/entities                     - List entities for client
GET    /api/v1/aeo/recommendations              - Get AEO optimization suggestions
```

### Influencers
```
GET    /api/v1/influencers                      - List influencers
POST   /api/v1/influencers/search               - Search/rank influencers by niche
POST   /api/v1/influencers/campaigns            - Create influencer campaign
GET    /api/v1/influencers/campaigns/{id}/roi   - Get campaign ROI
```

### Competitors
```
GET    /api/v1/competitors                      - List competitors for client
POST   /api/v1/competitors                      - Add competitor
GET    /api/v1/competitors/{id}/metrics         - Get competitor metrics
```

### Reports
```
POST   /api/v1/reports/export                   - Generate report (async)
GET    /api/v1/reports/{id}/download            - Download report file
GET    /api/v1/reports                          - List generated reports
```

### Copilot
```
POST   /api/v1/copilot/chat                     - Send message to AI assistant
GET    /api/v1/copilot/conversations            - List chat conversations
```

---

## ML Recommendation Engine Details

### Feature Engineering
Extract features from `daily_metrics` and `campaigns`:

```python
features = [
    'spend',
    'impressions',
    'clicks',
    'conversions',
    'cpa',
    'cpc',
    'ctr',
    'roas',
    'day_of_week',
    'hour_of_day',
    'campaign_age_days',
    'spend_trend_7d',      # % change in spend
    'cpa_trend_7d',        # % change in CPA
    'ctr_trend_7d',        # % change in CTR
    'budget_pacing',       # % of budget spent vs expected
    'days_since_creative_refresh',
    'audience_size',
    'geo',
    'platform',
]
```

### Optimization Objectives
1. **Minimize CPA** (target_cpa constraint)
2. **Maximize ROAS** (target_roas constraint)
3. **Minimize CPC** (for traffic campaigns)
4. **Maximize LTV/CAC** (long-term value)

### Recommendation Actions

#### Budget Recommendations
```python
{
    "action": "increase_budget",
    "campaign_id": "uuid",
    "reason": "CPA 15% below target with 200+ conversions, high budget utilization",
    "confidence": 0.87,
    "estimated_impact": {
        "additional_conversions": 120,
        "additional_revenue": 240000
    },
    "suggested_new_budget": 150000  # from 100000
}
```

#### Bid Recommendations
```python
{
    "action": "lower_bid",
    "campaign_id": "uuid",
    "reason": "CPA 28% above target for 3 consecutive days",
    "confidence": 0.81,
    "estimated_impact": {
        "savings": 42000,
        "conversion_drop": 8  # acceptable tradeoff
    },
    "suggested_new_bid": 45  # from 60
}
```

#### Creative Recommendations
```python
{
    "action": "rotate_creative",
    "campaign_id": "uuid",
    "reason": "CTR declined 35% over last 5 days (creative fatigue)",
    "confidence": 0.73,
    "estimated_impact": {
        "ctr_improvement": "+20%",
        "cpa_improvement": "-12%"
    },
    "suggested_creatives": ["creative_id_123", "creative_id_456"]
}
```

#### Campaign Pause Recommendations
```python
{
    "action": "pause_campaign",
    "campaign_id": "uuid",
    "reason": "CPA >2x target for 7+ days, declining ROAS, high budget burn",
    "confidence": 0.92,
    "estimated_impact": {
        "savings": 180000,
        "conversion_loss": 45  # but unprofitable
    }
}
```

### ML Models (Phase 2/3)

#### CPA Predictor
- **Algorithm:** XGBoost Regressor
- **Input:** Features above
- **Output:** Predicted CPA for next 7 days
- **Use case:** Proactive budget/bid adjustments

#### Budget Elasticity Model
- **Algorithm:** Multi-armed bandit (Thompson Sampling)
- **Input:** Historical spend vs conversions curve
- **Output:** Optimal budget allocation across campaigns
- **Use case:** Portfolio optimization

#### Creative Fatigue Detector
- **Algorithm:** Time-series anomaly detection (Prophet or ARIMA)
- **Input:** Daily CTR, impressions
- **Output:** Fatigue probability score
- **Use case:** Creative refresh timing

---

## Verification & Testing Strategy

### Unit Tests
- Services layer (business logic)
- Repositories (data access)
- ML models (prediction accuracy)

### Integration Tests
- API endpoints (FastAPI TestClient)
- Connectors (mock DSP responses)
- Database operations (async SQLAlchemy)

### End-to-End Tests
1. **User Flow: Create Campaign**
   - Register agency account
   - Connect Google Ads
   - Create campaign via UI
   - Verify campaign synced to DB
   - Check metrics ingestion

2. **User Flow: Optimization**
   - Seed campaign with metrics data
   - Run optimizer
   - Verify recommendations generated
   - Apply recommendation
   - Verify campaign updated

3. **User Flow: Report Export**
   - Select client and date range
   - Generate report
   - Download PDF
   - Verify metrics accuracy

### Local Development Testing
```bash
# Start services
docker-compose up -d

# Run backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Run frontend
cd frontend
npm install
npm run dev

# Run workers
celery -A app.workers.celery_app worker --loglevel=info

# Access
Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
```

### Sample Seeded Data
```sql
-- Agency
INSERT INTO organizations VALUES ('org-1', 'Apex Media Agency', 'agency', NOW(), '{}');

-- Users
INSERT INTO users VALUES 
    ('user-1', 'admin@apexmedia.com', 'hashed_pw', 'John Doe', 'agency_admin', 'org-1', NOW()),
    ('user-2', 'trader@apexmedia.com', 'hashed_pw', 'Jane Smith', 'trader', 'org-1', NOW());

-- Clients
INSERT INTO clients VALUES 
    ('client-1', 'org-1', 'Nike Running', 'Sports', NOW()),
    ('client-2', 'org-1', 'Tesla Motors', 'Automotive', NOW());

-- Platform Connections
INSERT INTO platform_connections VALUES 
    ('conn-1', 'client-1', 'google_ads', 'nike-ads-123', 'encrypted_token', 'active', NOW(), NOW()),
    ('conn-2', 'client-1', 'meta', 'act_456789', 'encrypted_token', 'active', NOW(), NOW());

-- Campaigns
INSERT INTO campaigns VALUES 
    ('camp-1', 'client-1', 'conn-1', 'ext-123', 'Nike Air Max - Search', 'active', 'conversions', 50000, 1500000, '2026-04-01', '2026-05-31', 250, NULL, NOW(), NOW()),
    ('camp-2', 'client-1', 'conn-2', 'ext-456', 'Nike Brand Awareness - Facebook', 'active', 'awareness', 30000, NULL, '2026-04-01', '2026-05-31', NULL, NULL, NOW(), NOW());

-- Metrics (last 30 days)
INSERT INTO daily_metrics (id, campaign_id, date, spend, impressions, clicks, conversions, cpa, cpc, ctr, roas)
SELECT 
    gen_random_uuid(),
    'camp-1',
    CURRENT_DATE - (30 - generate_series) * INTERVAL '1 day',
    45000 + random() * 10000,
    500000 + random() * 100000,
    12000 + random() * 3000,
    180 + random() * 40,
    240 + random() * 20,
    3.5 + random() * 0.5,
    0.024,
    3.2 + random() * 0.8
FROM generate_series(0, 29);
```

---

## Security Considerations

### Multi-Tenancy Isolation
- **Row-Level Security (RLS)** in PostgreSQL
- Every query filtered by `organization_id` or `client_id`
- Middleware injects tenant context from JWT

### Authentication & Authorization
- JWT with short expiry (15 min) + refresh tokens (7 days)
- Password hashing with bcrypt (cost factor 12)
- RBAC enforced at API layer:
  - `Super Admin` → full access
  - `Agency Admin` → org-wide access
  - `Trader` → client access (via user_client_access)
  - `Analyst` → read-only
  - `Client Viewer` → single client, read-only

### Data Encryption
- Secrets (API keys, OAuth tokens) encrypted at rest (AES-256)
- TLS for all API communication
- Database connection encryption

### Audit Logging
- All mutations logged to `audit_logs` table
- Track user, timestamp, IP, action, resource, changes

### API Security
- Rate limiting (100 req/min per user)
- CORS whitelist
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy parameterized queries)

---

## Observability

### Logging
- Structured JSON logs (timestamp, level, service, tenant, user, trace_id)
- Log aggregation (Loki or CloudWatch)

### Metrics
- Prometheus metrics:
  - Request latency (p50, p95, p99)
  - Error rate
  - Campaign sync success rate
  - ML recommendation accuracy
  - Active users

### Tracing
- OpenTelemetry for distributed tracing
- Trace across FastAPI → Celery → DSP API calls

### Alerting
- PagerDuty/Opsgenie for critical alerts:
  - API error rate >5%
  - Database connection failures
  - DSP sync failures

---

## Scaling Roadmap

### Phase 1 (MVP) - Supports:
- 50 agencies
- 500 clients
- 10,000 campaigns
- Single region deployment

### Phase 2 - Supports:
- 500 agencies
- 5,000 clients
- 100,000 campaigns
- Read replicas for PostgreSQL
- Redis cluster
- Horizontal scaling (multiple FastAPI instances)

### Phase 3 - Enterprise Scale:
- 5,000+ agencies
- 50,000+ clients
- 1M+ campaigns
- Database sharding by organization
- ClickHouse for analytics queries
- Multi-region deployment
- CDN for frontend assets
- Kubernetes with auto-scaling

### Infrastructure Evolution
```
MVP:           Docker Compose (local/single server)
Phase 2:       Docker Swarm or ECS
Phase 3:       Kubernetes (EKS/GKE/AKS)
```

---

## Deployment Strategy

### Local Development
```bash
docker-compose up
```

### Staging
- Deploy to cloud VM (AWS EC2 or GCP Compute)
- Use managed PostgreSQL (RDS/Cloud SQL)
- Use managed Redis (ElastiCache/Memorystore)
- CI/CD via GitHub Actions:
  - Run tests
  - Build Docker images
  - Push to container registry
  - Deploy to staging

### Production
- Kubernetes cluster
- Helm charts for deployments
- Blue-green deployments
- Database migrations via Alembic (automated in CI/CD)
- Secrets management (AWS Secrets Manager or Vault)

---

## Success Metrics (Product KPIs)

### Adoption
- Agencies onboarded per month
- Active users per week
- Campaigns managed on platform

### Engagement
- Daily active users
- Time spent in platform
- Recommendations applied rate

### Business Impact
- Average CPA improvement (%) for clients using optimizer
- Average ROAS improvement (%)
- Time saved vs fragmented tools (hours/week)

### Platform Health
- API uptime (target: 99.9%)
- Campaign sync latency (target: <5 min)
- Recommendation generation time (target: <30 sec)

---

## Next Steps (Post-Plan Approval)

1. **Create project structure** (folders, placeholder files)
2. **Set up Docker Compose** with PostgreSQL, Redis, FastAPI, Next.js
3. **Implement database schema** (SQLAlchemy models + Alembic migration)
4. **Build authentication system** (JWT, RBAC, tenant middleware)
5. **Create Google Ads connector** (OAuth2, campaign sync)
6. **Build campaign CRUD API** and frontend pages
7. **Implement ML optimizer v1** (rule-based recommendations)
8. **Develop dashboard UI** (KPI cards, charts, campaign table)
9. **Add reporting engine** (PDF export)
10. **Write tests and documentation**

---

## Summary

This plan delivers a **production-grade, enterprise SaaS platform** for media agencies to:

- Manage multi-channel ad campaigns from a single UI
- Optimize CPA/ROAS using ML-powered recommendations
- Gain brand/competitor intelligence
- Manage influencer campaigns
- Improve SEO/AEO visibility
- Export white-label client reports
- Use AI copilot for strategic decisions

**Architecture:** Clean layered backend (FastAPI), modern frontend (Next.js), proper multi-tenancy, RBAC, observability, scalability patterns.

**MVP timeline:** 6-8 weeks to ship core platform with Google Ads/Meta integrations, campaign management, ML optimizer, and reporting.

**Not a toy** - following SOLID principles, production best practices, and designed for scale from day one.
