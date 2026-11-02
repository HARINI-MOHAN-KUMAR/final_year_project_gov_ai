# GovGuide AI 🇮🇳
> Final Year Project — AI-Powered Citizen Advisory Platform for Indian Government Schemes

---

## 🚀 How to Run the Project

You can run the project using any of the following methods:

### Option 1: Double-Click Launcher (Windows)
Double-click:
- **`run_dev.bat`** — Starts both Backend (port 8000) and Frontend (port 5173).
- **`run_fast.bat`** — Single-port mode (builds frontend, serves everything from backend at port 8000).

---

### Option 2: Unified Python Launcher (Cross-Platform)
```bash
# Standard dev mode:
python run.py

# Single-port mode:
python run.py --fast

# Run the full 81-test test suite:
python run.py --test
```

---

### Option 3: PowerShell Script
```powershell
.\run_dev.ps1
```

---

### Option 4: Makefile
```bash
make run          # Starts full stack
make test         # Runs all 81 tests
make build        # Builds frontend
```

---

## 🌐 URLs
- **Frontend App:** [http://127.0.0.1:5173](http://127.0.0.1:5173) (or `http://127.0.0.1:8000` in fast mode)
- **Backend API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)
