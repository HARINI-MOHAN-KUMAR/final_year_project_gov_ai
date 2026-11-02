# ==============================================================================
# GovGuide AI - Root Makefile
# ==============================================================================

.PHONY: all help install build test test-unit test-api run run-backend run-frontend clean

PYTHON ?= .venv/Scripts/python.exe
PYTEST ?= .venv/Scripts/pytest.exe
UVICORN ?= .venv/Scripts/uvicorn.exe
NPM ?= npm.cmd

all: install build test
	@echo "=================================================="
	@echo " GovGuide AI successfully built and tested!"
	@echo " Run 'make run' to launch both backend and frontend."
	@echo "=================================================="

help:
	@echo "GovGuide AI - Available Targets:"
	@echo "  make               - Install dependencies, build frontend, and run tests"
	@echo "  make install       - Install Python and Node.js dependencies"
	@echo "  make build         - Build Vite frontend for production"
	@echo "  make test          - Run full 81-test test suite"
	@echo "  make test-unit     - Run unit tests (Eligibility + OCR parsers)"
	@echo "  make test-api      - Run API integration tests"
	@echo "  make run           - Run both Backend (port 8000) and Frontend (port 5173)"
	@echo "  make run-backend   - Start FastAPI backend with Uvicorn"
	@echo "  make run-frontend  - Start Vite frontend development server"
	@echo "  make clean         - Remove caches, test DBs, and build dist"

install:
	@echo "Installing backend requirements..."
	cd govguide-ai/backend && $(PYTHON) -m pip install -r requirements.txt
	@echo "Installing frontend packages..."
	cd govguide-ai/frontend && $(NPM) install

build:
	@echo "Building frontend..."
	cd govguide-ai/frontend && $(NPM) run build

test:
	@echo "Running all 81 tests..."
	cd govguide-ai/backend && $(PYTEST) tests -v

test-unit:
	@echo "Running unit tests (Rule Engine + OCR Parsers)..."
	cd govguide-ai/backend && $(PYTEST) tests/test_eligibility_engine.py tests/test_ocr_parsers.py -v

test-api:
	@echo "Running API integration tests..."
	cd govguide-ai/backend && $(PYTEST) tests/test_api.py -v

run-backend:
	@echo "Starting GovGuide AI FastAPI backend on http://localhost:8000..."
	cd govguide-ai/backend && $(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	@echo "Starting GovGuide AI Vite frontend on http://localhost:5173..."
	cd govguide-ai/frontend && $(NPM) run dev

run:
	@echo "Starting GovGuide AI Full Stack (Powershell launcher)..."
	powershell -ExecutionPolicy Bypass -File ./run_dev.ps1

clean:
	@echo "Cleaning caches and artifacts..."
	-rmdir /s /q govguide-ai\frontend\dist
	-del /f /q govguide-ai\backend\test_govguide.db
	-del /f /q govguide-ai\backend\govguide.db
