"""
Unified System Orchestrator & Launcher for IS-Recommender (SIH26108).
Launches both the FastAPI backend and Vite React frontend concurrently with automated health checks.
"""
import sys
import os
import time
import subprocess
import webbrowser
import urllib.request
import signal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = REPO_ROOT / "frontend"

def check_backend_ready(url="http://127.0.0.1:8000/api/v1/health", max_retries=30, delay=1.0):
    """Waits for the FastAPI backend to finish warming models and become healthy."""
    print("[Launcher] Waiting for IS-Recommender API to warm up models & FAISS index...")
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    print(f"[Launcher] Backend is HEALTHY and operational (Attempt {attempt}).")
                    return True
        except Exception:
            pass
        time.sleep(delay)
        print(f"[Launcher] Still waiting for backend... ({attempt}/{max_retries}s)")
    return False

def main():
    print("=" * 80)
    print("      INDIAN STANDARDS (BIS) AI RECOMMENDATION ENGINE (SIH26108)")
    print("           Bureau of Indian Standards & Government e-Marketplace")
    print("=" * 80)

    # 1. Start FastAPI Backend Server
    print("\n[1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000"]
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(REPO_ROOT),
        stdout=None,
        stderr=None
    )

    # 2. Wait for Backend to be Healthy
    ready = check_backend_ready()
    if not ready:
        print("[Launcher] Warning: Backend took longer than expected to report healthy, continuing...")

    # 3. Start Frontend Dev Server
    print("\n[2/3] Starting Vite React Frontend on http://localhost:5173 ...")
    npm_executable = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_executable, "run", "dev"],
        cwd=str(FRONTEND_DIR),
        stdout=None,
        stderr=None
    )

    time.sleep(2)
    portal_url = "http://localhost:5173"
    api_docs_url = "http://127.0.0.1:8000/docs"

    print("\n" + "=" * 80)
    print(f" [SUCCESS] IS-RECOMMENDER PLATFORM RUNNING:")
    print(f"   * Web Portal (UI)     : {portal_url}")
    print(f"   * Swagger API Docs    : {api_docs_url}")
    print(f"   * Health Endpoint     : http://127.0.0.1:8000/api/v1/health")
    print("=" * 80)
    print(" Press Ctrl+C to stop both servers.\n")

    # 4. Open Browser
    try:
        webbrowser.open(portal_url)
    except Exception:
        pass

    def shutdown(signum, frame):
        print("\n[Launcher] Shutting down IS-Recommender services...")
        try:
            frontend_proc.terminate()
        except Exception:
            pass
        try:
            backend_proc.terminate()
        except Exception:
            pass
        print("[Launcher] Shutdown complete. Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    try:
        # Keep orchestrator alive
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("[Launcher] Backend process exited unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("[Launcher] Frontend process exited unexpectedly.")
                break
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()
