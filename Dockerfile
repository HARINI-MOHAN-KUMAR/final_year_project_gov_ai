# ==============================================================================
# GovGuide AI - Multi-Stage Production Dockerfile
# ==============================================================================

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY govguide-ai/frontend/package*.json ./
RUN npm ci --silent || npm install

COPY govguide-ai/frontend ./
RUN npm run build

# Stage 2: Production Python Backend + Built Frontend
FROM python:3.11-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies (including tesseract for OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    tesseract-ocr-tam \
    tesseract-ocr-ben \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY govguide-ai/backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend application code
COPY govguide-ai/backend ./backend
COPY govguide-ai/data ./data
COPY govguide-ai/.env.example ./govguide-ai/.env.example

# Copy built frontend assets into the expected directory
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Ensure backend .env exists if not provided via environment variables
RUN if [ ! -f ./backend/.env ]; then cp ./govguide-ai/.env.example ./backend/.env; fi

WORKDIR /app/backend

EXPOSE 8000

# Start Uvicorn bound to 0.0.0.0 and dynamically respect $PORT (for Render/Railway/Fly.io/Docker)
CMD sh -c "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
