# 🚀 OmniGrowth OS

**Unified AI Operating System for Media Agencies and Brand Growth Teams**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.1.0-000000?logo=next.js)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://www.postgresql.org/)

---

## 🎯 Vision

Replace fragmented agency tooling (DSPs, ad managers, analytics dashboards, SEO tools, influencer platforms, reporting tools) with **one unified platform** featuring:

- **Multi-channel campaign management** (Google Ads, Meta, DV360, Trade Desk, LinkedIn, TikTok, Amazon)
- **ML-powered optimization engine** for CPA/CPC/ROAS optimization
- **Intelligence layers**: Brand health, competitor tracking, influencer CRM, SEO/AEO optimization
- **AI Copilot** with RAG for strategic insights
- **White-label reporting** for client exports

> **Not a toy dashboard** — this is *"Bloomberg Terminal + HubSpot + Trade Desk + SEMrush + AI Copilot for Agencies"*

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (if running locally)
- Node.js 20+

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd omniAgent
cp .env.example .env
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Project Structure

```
omniAgent/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── core/     # Security, RBAC, tenant middleware ✅
│   │   ├── db/       # SQLAlchemy models & session ✅
│   │   ├── api/      # API endpoints
│   │   ├── services/ # Business logic
│   │   ├── connectors/ # DSP integrations
│   │   ├── ml/       # ML optimization engine
│   │   └── workers/  # Celery tasks
│   └── requirements.txt
│
├── frontend/          # Next.js frontend
│   ├── app/          # App Router pages
│   ├── components/   # React components
│   └── lib/          # Utilities & stores
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔑 Key Features

### 1. Multi-Tenant SaaS Architecture
- Agencies → Clients → Ad Accounts hierarchy
- Row-Level Security (RLS) in PostgreSQL
- 5 roles: Super Admin, Agency Admin, Trader, Analyst, Viewer

### 2. Unified Campaign Management
- Manage campaigns across multiple DSPs
- Editable campaign grid with filters
- Real-time budget pacing alerts

### 3. ML Optimization Engine
- Rule-based optimizer (v1): Budget/bid recommendations
- Advanced models (v2): XGBoost, creative fatigue detection
- Automated execution (optional)

### 4. Intelligence Layers
- Brand health & competitor tracking
- Influencer CRM with ROI tracking
- SEO/AEO optimization modules

### 5. AI Copilot
- RAG over metrics and campaigns
- Natural language queries
- Strategic recommendations

### 6. White-Label Reporting
- Automated client reports (PDF/Excel)
- Customizable templates

---

## 🛠️ Development

### Backend (Local)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (Local)

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

---

## 📊 Implementation Status

**Overall MVP Completion: ~30%**

✅ **Completed:**
- Infrastructure setup (Docker, configs)
- Backend core (FastAPI, security, RBAC, tenant middleware)
- Database session management

🚧 **In Progress:**
- Database models
- Authentication system

📋 **Remaining:**
- Campaign management APIs
- ML optimizer
- Frontend implementation
- DSP connectors

See [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) for detailed checklist.

---

## 🗺️ Roadmap

### Phase 1: MVP (6-8 weeks) - 30% Complete
- Multi-tenant SaaS foundation
- Auth system with RBAC
- Google Ads + Meta connectors
- Campaign management UI
- ML optimizer (rule-based v1)

### Phase 2: Intelligence (4-6 weeks)
- SEO & AEO modules
- Competitor intelligence
- Influencer CRM
- Additional DSP connectors

### Phase 3: AI Automation (4-6 weeks)
- AI Copilot with RAG
- Advanced ML models
- Automated execution
- Production deployment

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: [/docs](./docs/)

---

**Built with ❤️ for media agencies**
