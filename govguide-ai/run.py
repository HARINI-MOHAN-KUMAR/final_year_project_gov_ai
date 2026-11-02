#!/usr/bin/env python3
"""
GovGuide AI - Unified Project Launcher
Cross-platform runner for the FastAPI backend and React frontend.

Usage:
    python run.py          # Standard development mode (Backend: 8000, Frontend: 5173)
    python run.py --fast   # Single-port mode (builds frontend, serves all via port 8000)
    python run.py --test   # Runs the full 81-test test suite
"""

import sys
import os
import shutil
import subprocess
import time
import signal
import webbrowser
import urllib.request
from pathlib import Path

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Windows color support
if sys.platform == "win32":
    os.system("color")


def print_step(msg):
    print(f"{CYAN}{BOLD}==>{RESET} {BOLD}{msg}{RESET}")


def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_warn(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")


def print_err(msg):
    print(f"{RED}✗ {msg}{RESET}")


def locate_directories():
    base = Path(__file__).resolve().parent
    if (base / "backend").is_dir() and (base / "frontend").is_dir():
        govguide_dir = base
    elif (base / "govguide-ai" / "backend").is_dir():
        govguide_dir = base / "govguide-ai"
    else:
        print_err(f"Could not locate govguide-ai directory from {base}")
        sys.exit(1)

    backend_dir = govguide_dir / "backend"
    frontend_dir = govguide_dir / "frontend"
    env_example = govguide_dir / ".env.example"
    return govguide_dir, backend_dir, frontend_dir, env_example


def get_venv_python(backend_dir):
    if sys.platform == "win32":
        venv_py = backend_dir / ".venv" / "Scripts" / "python.exe"
    else:
        venv_py = backend_dir / ".venv" / "bin" / "python"
    return venv_py


def ensure_backend_env(backend_dir, env_example):
    target_env = backend_dir / ".env"
    if not target_env.exists() and env_example.exists():
        shutil.copy(env_example, target_env)
        print_success("Created backend .env from template.")


def ensure_backend_venv(backend_dir):
    venv_py = get_venv_python(backend_dir)
    if not venv_py.exists():
        print_step("Creating Python virtual environment in .venv...")
        subprocess.check_call([sys.executable, "-m", "venv", str(backend_dir / ".venv")])
        print_success("Virtual environment created.")

    # Check if core dependencies are installed
    check_code = "import fastapi, uvicorn, sqlalchemy, aiosqlite"
    res = subprocess.run([str(venv_py), "-c", check_code], capture_output=True)
    if res.returncode != 0:
        print_step("Installing backend dependencies from requirements.txt...")
        req_file = backend_dir / "requirements.txt"
        subprocess.check_call([str(venv_py), "-m", "pip", "install", "-r", str(req_file)])
        print_success("Backend dependencies installed.")

    return venv_py


def ensure_frontend(frontend_dir):
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    node_modules = frontend_dir / "node_modules"
    vite_bin = frontend_dir / "node_modules" / "vite"
    if not node_modules.exists() or not vite_bin.exists():
        print_step("Installing frontend dependencies with npm install...")
        subprocess.check_call([npm_cmd, "install"], cwd=str(frontend_dir))
        print_success("Frontend dependencies installed.")
    return npm_cmd


def run_tests(backend_dir, venv_py):
    print_step("Running test suite...")
    cmd = [str(venv_py), "-m", "pytest", "tests", "-v"]
    ret = subprocess.call(cmd, cwd=str(backend_dir))
    sys.exit(ret)


def wait_for_url(url, timeout=40):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status in (200, 301, 302, 304):
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main():
    fast_mode = "--fast" in sys.argv
    test_mode = "--test" in sys.argv

    govguide_dir, backend_dir, frontend_dir, env_example = locate_directories()
    venv_py = ensure_backend_venv(backend_dir)
    ensure_backend_env(backend_dir, env_example)

    if test_mode:
        run_tests(backend_dir, venv_py)
        return

    npm_cmd = ensure_frontend(frontend_dir)

    if fast_mode:
        print_step("Building frontend for single-port deployment...")
        subprocess.check_call([npm_cmd, "run", "build"], cwd=str(frontend_dir))
        print_success("Frontend built.")

    processes = []

    def shutdown(signum=None, frame=None):
        print(f"\n{YELLOW}Stopping servers...{RESET}")
        for p in processes:
            try:
                if sys.platform == "win32":
                    subprocess.call(["taskkill", "/F", "/T", "/PID", str(p.pid)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    p.terminate()
            except Exception:
                pass
        print(f"{GREEN}All servers stopped. Goodbye!{RESET}")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    print_step("Starting FastAPI backend on port 8000...")
    backend_cmd = [
        str(venv_py), "-m", "uvicorn", "app.main:app",
        "--reload", "--host", "127.0.0.1", "--port", "8000"
    ]
    backend_proc = subprocess.Popen(backend_cmd, cwd=str(backend_dir))
    processes.append(backend_proc)

    frontend_url = "http://127.0.0.1:8000" if fast_mode else "http://127.0.0.1:5173"

    if not fast_mode:
        print_step("Starting Vite frontend development server on port 5173...")
        frontend_cmd = [npm_cmd, "run", "dev", "--", "--host", "127.0.0.1"]
        frontend_proc = subprocess.Popen(frontend_cmd, cwd=str(frontend_dir))
        processes.append(frontend_proc)

    print_step("Waiting for services to become ready...")
    if not wait_for_url("http://127.0.0.1:8000/health", timeout=30):
        print_err("Backend failed to start. Check terminal output for errors.")
        shutdown()

    if not fast_mode:
        if not wait_for_url(frontend_url, timeout=30):
            print_err("Frontend failed to start. Check terminal output for errors.")
            shutdown()

    print(f"\n{GREEN}{BOLD}============================================================{RESET}")
    print(f"{GREEN}{BOLD}  GovGuide AI is running!{RESET}")
    print(f"  {BOLD}Frontend:{RESET}  {frontend_url}")
    print(f"  {BOLD}Backend:{RESET}   http://127.0.0.1:8000")
    print(f"  {BOLD}API Docs:{RESET}  http://127.0.0.1:8000/api/docs")
    print(f"{GREEN}{BOLD}============================================================{RESET}")
    print(f"{YELLOW}Press Ctrl+C to stop all servers.{RESET}\n")

    try:
        webbrowser.open(frontend_url)
    except Exception:
        pass

    try:
        while True:
            for p in processes:
                if p.poll() is not None:
                    print_err(f"A process terminated unexpectedly (exit code {p.returncode}).")
                    shutdown()
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
