# 🚀 GovGuide AI - Deployment Guide

This guide covers the best ways to deploy GovGuide AI into production.

---

## 🌟 Recommended Deployment Options

| Method | Best For | Cost | Setup Time | Notes |
|---|---|---|---|---|
| **Render (Single Web Service)** | College/Final Year Project Showcase | Free | ~5 mins | Uses `Dockerfile` to build React frontend + FastAPI into 1 service |
| **Railway** | Production-ready full stack | Free trial / \$5 mo | ~5 mins | 1-click Docker deploy with persistent volume |
| **Vercel + Render** | Split Architecture | Free | ~10 mins | Frontend on Vercel CDN, Backend on Render |
| **VPS (Ubuntu / Docker)** | Complete ownership (AWS, DO, Linode) | \$4-6 / mo | ~15 mins | Uses `docker-compose.yml` |

---

## Option 1: Render.com (Easiest & Free)

Since the project uses a multi-stage `Dockerfile`, Render will automatically:
1. Build the Vite/React frontend
2. Install Python backend dependencies & Tesseract OCR
3. Serve both API and Frontend under a single HTTPS domain!

### Steps:
1. Push this project to your GitHub repository.
2. Sign in to [Render.com](https://render.com) with GitHub.
3. Click **New +** -> **Web Service**.
4. Connect your `final_year_project` (or `govguide-ai`) repo.
5. Select **Docker** as the environment (Render auto-detects `Dockerfile`).
6. Set the Environment Variables:
   - `SECRET_KEY`: `<Generate a 32+ character random string>`
   - `LLM_PROVIDER`: `mock` (or `gemini` if you have a Gemini API key)
   - `GEMINI_API_KEY`: `<Your Gemini Key if using gemini>`
   - `DEBUG`: `false`
7. Click **Create Web Service**.
8. Once deployed, Render gives you a live URL like `https://govguide-ai.onrender.com`.

---

## Option 2: Railway.app (Fastest Docker Deploy)

1. Push your repo to GitHub.
2. Go to [Railway.app](https://railway.app) and click **New Project** -> **Deploy from GitHub repo**.
3. Railway detects the `Dockerfile` and builds both frontend and backend.
4. Under **Settings** -> **Networking**, click **Generate Domain**.
5. Under **Variables**, add:
   - `SECRET_KEY`: `<random string>`
   - `PORT`: `8000`
   - `DEBUG`: `false`

---

## Option 3: VPS / Local Server with Docker Compose

If you have a Linux VPS (AWS EC2, DigitalOcean, Linode, Ubuntu):

```bash
# 1. Clone repository
git clone <your-repo-url>
cd final_year_project

# 2. Build and launch with docker-compose
docker compose up -d --build

# 3. Check logs
docker compose logs -f
```

The application will be live at `http://your-server-ip:8000`.

---

## Option 4: Split Frontend (Vercel) + Backend (Render/Railway)

### Backend:
1. Deploy `govguide-ai/backend` to Render as a Python Web Service.
2. Set Build Command: `pip install -r requirements.txt`
3. Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set `CORS_ORIGINS`: `["https://your-frontend.vercel.app"]`

### Frontend:
1. Deploy `govguide-ai/frontend` to [Vercel](https://vercel.com).
2. Framework Preset: **Vite**.
3. Set Environment Variable:
   - `VITE_API_BASE_URL`: `https://your-backend.onrender.com`
