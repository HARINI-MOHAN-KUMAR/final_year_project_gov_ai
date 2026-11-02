# GovGuide AI 🇮🇳

> **Final Year Project** — An AI-powered citizen advisory platform for discovering and applying to Indian government schemes.

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18-61dafb)](https://react.dev)
[![Vite 6](https://img.shields.io/badge/Vite-6-646cff)](https://vitejs.dev)
[![Tests](https://img.shields.io/badge/Tests-81%20passing-brightgreen)](#testing)

> **⚠️ Advisory Disclaimer:** GovGuide AI is a student research project intended for educational and informational purposes only. It is **not** affiliated with or endorsed by any government body. Eligibility results and scheme information are indicative only — always verify with official government portals (india.gov.in, myscheme.gov.in) before applying.

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Configuration](#configuration)
- [Helplines & Official Portals](#helplines--official-portals)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Scheme Discovery** | Browse 50+ central & state government schemes with filters |
| ✅ **AI Eligibility Check** | Rule-based engine + ML model evaluates your eligibility |
| 📄 **OCR Document Parser** | Upload Aadhaar, income certificates, ration cards — extract key fields |
| 💬 **AI Chat Assistant** | RAG-grounded Q&A about government schemes |
| 📊 **Application Tracker** | Track your scheme applications end-to-end |
| 👤 **Citizen Profile** | Store your profile once, auto-fill eligibility checks |
| 🌐 **Multilingual** | English, हिन्दी, தமிழ், বাংলা |
| 🔐 **JWT Authentication** | Secure login/register with role-based access |
| 🛡️ **Admin Dashboard** | Manage scheme catalog and view platform KPIs |

---

## 🏗️ Architecture

```
govguide-ai/
├── backend/          FastAPI + SQLAlchemy (async) + SQLite
│   ├── app/
│   │   ├── api/      REST endpoints (schemes, auth, eligibility, OCR, chat, applications)
│   │   ├── core/     Config, security, database setup
│   │   ├── models/   SQLAlchemy ORM models
│   │   ├── schemas/  Pydantic request/response schemas
│   │   ├── services/ Business logic (eligibility engine, LLM, RAG, scheduler)
│   │   └── ocr/      Document OCR processing
│   └── tests/        81 unit + integration tests
├── frontend/         React 18 + Vite 6 + Tailwind CSS
│   └── src/
│       ├── pages/    Home, Schemes, Eligibility, OCR, Chat, Applications, Profile, Admin
│       ├── components/ Navbar, Footer, SchemeCard, EligibilityModal
│       ├── store/    Zustand auth store
│       ├── api/      Axios client with JWT interceptors
│       └── i18n/     Multilingual translations
└── data/             schemes.json — 50+ schemes with eligibility rules
```

### Tech Stack

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com) — async REST API
- [SQLAlchemy 2 + aiosqlite](https://docs.sqlalchemy.org) — async ORM (SQLite default, PostgreSQL ready)
- [Pydantic v2](https://docs.pydantic.dev) — data validation
- [python-jose](https://python-jose.readthedocs.io) + [passlib](https://passlib.readthedocs.io) — JWT auth + bcrypt hashing
- [APScheduler](https://apscheduler.readthedocs.io) — background jobs (scheme sync)
- [scikit-learn + pandas + numpy](https://scikit-learn.org) — ML eligibility model
- [pytesseract + Pillow](https://pypi.org/project/pytesseract/) — OCR document parsing
- [fuzzywuzzy](https://pypi.org/project/fuzzywuzzy/) — fuzzy text matching

**Frontend:**
- [React 18](https://react.dev) + [React Router 6](https://reactrouter.com) — SPA routing
- [Vite 6](https://vitejs.dev) — lightning-fast build tool
- [Tailwind CSS 3](https://tailwindcss.com) — utility-first styling
- [Zustand](https://zustand-demo.pmnd.rs) — lightweight state management
- [Axios](https://axios-http.com) — HTTP client with JWT interceptors
- [Lucide React](https://lucide.dev) — icon library

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| npm | 9+ | (comes with Node.js) |
| Git | any | [git-scm.com](https://git-scm.com) |

> **Optional:** [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) for document scanning (Windows installer available). Without it, OCR returns demo/mock data.

---

### 1. Clone & Setup Backend

```powershell
# Navigate to the project
cd govguide-ai/backend

# Create virtual environment
python -m venv .venv

# Activate it (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

> **Note:** If `requirements.txt` is missing, install manually:
> ```
> pip install fastapi uvicorn sqlalchemy aiosqlite pydantic[email] pydantic-settings python-jose[cryptography] passlib "bcrypt<4.0.0" python-multipart aiofiles httpx scikit-learn numpy pandas joblib pytest pytest-asyncio apscheduler python-dotenv fuzzywuzzy Pillow greenlet email-validator
> ```

### 2. Configure Environment

```powershell
# Copy the template (the Windows launcher does this automatically)
Copy-Item ..\.env.example .\.env

# Edit .env as needed (set LLM_PROVIDER, API keys, etc.)
notepad .\.env
```

Key settings in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (set) | JWT signing key — change in production! |
| `LLM_PROVIDER` | `mock` | `mock` / `gemini` / `openai` / `anthropic` |
| `GEMINI_API_KEY` | empty | Required only if `LLM_PROVIDER=gemini` |
| `DATABASE_URL` | `sqlite:///./govguide.db` | Switch to PostgreSQL for production |
| `TESSERACT_CMD` | (Windows path) | Path to tesseract.exe |

### 3. Start the Backend

```powershell
# From govguide-ai/backend/
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

✅ Backend is running at **http://localhost:8000**
- API Docs (Swagger): http://localhost:8000/api/docs
- Health check: http://localhost:8000/health

### 4. Setup & Start Frontend

```powershell
# In a new terminal, from govguide-ai/frontend/
npm install
npm run dev
```

✅ Frontend is running at **http://localhost:5173**

---

### 🎯 One-Command Startup (Windows)

From the project root `final_year_project\`, run:

```powershell
# Start both backend and frontend (creates the virtual environment and installs missing dependencies)
.\run_dev.bat
```

The first run requires Python 3.11+ and Node.js 18+ on `PATH`; it installs dependencies if needed and creates the backend `.env` from `.env.example`. The development UI is at http://localhost:5173 and the API docs are at http://localhost:8000/api/docs.

To build the frontend and serve the full app from the backend on port 8000 instead:

```cmd
run_fast.bat
```

The PowerShell equivalents are `.\run_dev.ps1` and `.\run_dev.ps1 -Fast`.

---

## 📁 Project Structure

```
final_year_project/
├── govguide-ai/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/v1/         # Route handlers
│   │   │   │   ├── auth.py     # Register, login, profile
│   │   │   │   ├── schemes.py  # Scheme CRUD
│   │   │   │   ├── eligibility.py
│   │   │   │   ├── ocr.py
│   │   │   │   ├── chat.py
│   │   │   │   └── applications.py
│   │   │   ├── core/
│   │   │   │   ├── config.py   # Settings (pydantic-settings)
│   │   │   │   ├── database.py # Async engine + session
│   │   │   │   └── security.py # JWT + password hashing
│   │   │   ├── models/         # SQLAlchemy ORM
│   │   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── services/
│   │   │   │   ├── eligibility_engine.py  # Rule evaluator
│   │   │   │   ├── llm_service.py         # LLM abstraction
│   │   │   │   ├── rag_service.py         # RAG / keyword search
│   │   │   │   └── scheduler.py           # APScheduler jobs
│   │   │   └── ocr/
│   │   │       └── processor.py           # Tesseract + regex parsers
│   │   ├── tests/
│   │   │   ├── test_api.py              # 20 integration tests
│   │   │   ├── test_eligibility_engine.py # 26 unit tests
│   │   │   └── test_ocr_parsers.py      # 35 unit tests
│   │   ├── .env                # Local config (not committed)
│   │   └── requirements.txt
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── store/
│   │   │   ├── api/
│   │   │   └── i18n/
│   │   ├── package.json
│   │   └── vite.config.js
│   ├── data/
│   │   └── schemes.json        # 50+ government schemes
│   ├── docs/                   # Architecture & report docs
│   └── .env.example
├── Makefile                    # Root-level build commands
├── run_dev.ps1                 # PowerShell launcher
└── run_dev.bat                 # Batch launcher
```

---

## 📖 API Documentation

Once the backend is running, visit:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/auth/register` | Register citizen |
| `POST` | `/api/v1/auth/login` | Login (returns JWT) |
| `GET` | `/api/v1/auth/me` | Current user profile |
| `GET` | `/api/v1/schemes/` | List all schemes |
| `GET` | `/api/v1/schemes/{id}` | Scheme detail |
| `POST` | `/api/v1/eligibility/check` | Check eligibility for a scheme |
| `POST` | `/api/v1/eligibility/scan` | Scan eligibility across all schemes |
| `POST` | `/api/v1/ocr/upload` | Upload document for OCR |
| `POST` | `/api/v1/chat/message` | Send message to AI assistant |
| `GET` | `/api/v1/applications/` | List user's applications |
| `POST` | `/api/v1/applications/` | Track a new application |

---

## 🧪 Testing

```powershell
cd govguide-ai/backend

# Run all 81 tests
.\.venv\Scripts\pytest.exe tests/ -v

# Run specific test modules
.\.venv\Scripts\pytest.exe tests/test_eligibility_engine.py -v   # 26 tests
.\.venv\Scripts\pytest.exe tests/test_ocr_parsers.py -v          # 35 tests
.\.venv\Scripts\pytest.exe tests/test_api.py -v                  # 20 tests

# With coverage report
.\.venv\Scripts\pytest.exe tests/ --cov=app --cov-report=html
```

**Test Results:** ✅ 81 passed, 0 failed

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_api.py` | 20 | API integration |
| `test_eligibility_engine.py` | 26 | Rule engine unit tests |
| `test_ocr_parsers.py` | 35 | OCR regex + field extraction |

---

## ⚙️ Configuration

### LLM Provider Options

Set `LLM_PROVIDER` in `.env`:

| Provider | Key Required | Notes |
|----------|-------------|-------|
| `mock` | No | Returns canned responses — great for testing |
| `gemini` | `GEMINI_API_KEY` | Google Gemini 1.5 Flash (recommended) |
| `openai` | `OPENAI_API_KEY` | GPT-4o-mini |
| `anthropic` | `ANTHROPIC_API_KEY` | Claude 3 Haiku |

### Demo Accounts

After starting the backend, register at http://localhost:5173/register or use these quick-fill accounts on the Login page:

| Role | Email | Password |
|------|-------|----------|
| Citizen | demo@example.com | demo1234 |
| Admin | admin@example.com | admin123 |

> **Note:** First run — register these accounts via the UI or `/api/v1/auth/register`. For admin access, set `is_admin=True` in the SQLite DB after registration.

---

## 📞 Helplines & Official Portals

| Resource | Link / Number |
|----------|--------------|
| India Government Schemes | [india.gov.in](https://www.india.gov.in) |
| MyScheme Portal | [myscheme.gov.in](https://www.myscheme.gov.in) |
| PM-KISAN | [pmkisan.gov.in](https://pmkisan.gov.in) |
| National Helpline | **1800-11-0001** |
| PM-KISAN Helpline | **155261** |
| Women Helpline | **181** |
| Senior Citizen Helpline | **14567** |

---

## 🎓 Academic Context

This project was built as a **Final Year B.Tech/BCA Computer Science** capstone project exploring:
- Retrieval-Augmented Generation (RAG) for citizen services
- Rule-based + ML hybrid eligibility determination
- OCR-based document intelligence
- Multilingual government service delivery

**Supervisor:** [Your Supervisor's Name]  
**Institution:** [Your College/University Name]  
**Academic Year:** 2024–25

---

## 📄 License

This project is for academic use only. All government scheme data is sourced from publicly available information on official Indian government portals and is used for educational demonstration purposes.

---

*Made with ❤️ for Indian citizens | GovGuide AI — Empowering Every Citizen*
