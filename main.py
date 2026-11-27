
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.core.logging import configure_logging
from app.database.init_db import create_tables
from app.scheduler.email_scheduler import (
    sync_and_process_emails,
    start_scheduler,
)
from app.services.email_processor import EmailProcessor
from app.services.service_container import ServiceContainer

from app.api.users import router as users_router
from app.api.resume import router as resume_router
from app.api.jobs import router as jobs_router
from app.api import ats
from app.api.calendar import router as calendar_router

ROOT_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

FRONTEND_DIR = ROOT_DIR / "frontend"

configure_logging()

app = FastAPI(title="RESUAI")


def _read_log_tail(path: Path, lines: int = 200) -> str:
    if not path.exists():
        return "No log file yet."

    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        content = handle.readlines()

    return "".join(content[-lines:])


app.include_router(calendar_router)
app.include_router(users_router)
app.include_router(resume_router)
app.include_router(jobs_router)
app.include_router(ats.router)

@app.on_event("startup")
def startup():

    print("=" * 70)
    print("Starting Placement Copilot...")
    print("=" * 70)

    create_tables()

    ServiceContainer.initialize()

    sync_and_process_emails()

    start_scheduler()

    print("=" * 70)
    print("Application Started Successfully")
    print("=" * 70)


# -------------------------------------------------------
# Mount static frontend files
# -------------------------------------------------------
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    """Serve the main dashboard SPA."""
    dashboard_path = FRONTEND_DIR / "index.html"
    if dashboard_path.exists():
        return HTMLResponse(content=dashboard_path.read_text(encoding="utf-8"))

    # Fallback minimal page if frontend not built
    html = f"""
    <html>
      <head>
        <title>RESUAI</title>
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <style>
          :root{{--bg:#0f1724;--card:#0b1220;--muted:#94a3b8;--accent:#06b6d4;--glass:rgba(255,255,255,0.04)}}
          body{{margin:0;font-family:Inter,Segoe UI,Roboto,Arial,sans-serif;background:linear-gradient(180deg,#071025 0%, #081428 60%);color:#e6eef6}}
          .wrap{{max-width:1100px;margin:48px auto;padding:28px}}
          .hero{{display:flex;gap:24px;align-items:center}}
          .logo{{width:84px;height:84px;border-radius:14px;background:linear-gradient(135deg,var(--accent),#7c3aed);display:grid;place-items:center;font-weight:700;font-size:20px;color:#042029}}
          .title{{font-size:28px;margin:0 0 6px}}
          .lead{{color:var(--muted);margin:0 0 18px}}
          .cta{{display:flex;gap:12px}}
          .btn{{background:var(--accent);color:#042029;padding:10px 16px;border-radius:10px;text-decoration:none;font-weight:600}}
          .btn.secondary{{background:transparent;border:1px solid rgba(255,255,255,0.06);color:var(--muted)}}
        </style>
      </head>
      <body>
        <div class="wrap">
          <div class="hero">
            <div class="logo">RS</div>
            <div style="flex:1">
              <h1 class="title">RESUAI</h1>
              <p class="lead">Frontend not found. Make sure the <code>frontend/</code> folder exists.</p>
              <div class="cta">
                <a class="btn" href="/docs">API Docs</a>
                <a class="btn secondary" href="/health">Health Check</a>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Placement Copilot",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/logs-data")
def logs_data():
    """JSON endpoint for the frontend dashboard logs panel."""
    return {
        "out": _read_log_tail(LOGS_DIR / "app.out.log"),
        "err": _read_log_tail(LOGS_DIR / "app.err.log"),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/status", response_class=HTMLResponse)
def status_page():
    log_tail = _read_log_tail(LOGS_DIR / "app.out.log")
    html = f"""
    <html>
      <head><title>Status</title></head>
      <body style="font-family:Arial,sans-serif;padding:24px;line-height:1.5;">
        <h2>Service Status</h2>
        <p><strong>State:</strong> Running</p>
        <p><strong>Checked at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><a href="/">Home</a> | <a href="/logs">Logs</a></p>
        <pre style="background:#f5f5f5;padding:12px;border-radius:6px;white-space:pre-wrap;">{log_tail}</pre>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/logs", response_class=HTMLResponse)
def logs_page():
    out_log = _read_log_tail(LOGS_DIR / "app.out.log")
    err_log = _read_log_tail(LOGS_DIR / "app.err.log")
    html = f"""
    <html>
      <head><title>Logs</title></head>
      <body style="font-family:Arial,sans-serif;padding:24px;line-height:1.5;">
        <h2>Recent Logs</h2>
        <p><a href="/">Home</a> | <a href="/status">Status</a></p>
        <h3>Application output</h3>
        <pre style="background:#f5f5f5;padding:12px;border-radius:6px;white-space:pre-wrap;">{out_log}</pre>
        <h3>Errors</h3>
        <pre style="background:#f5f5f5;padding:12px;border-radius:6px;white-space:pre-wrap;">{err_log}</pre>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post("/graph/{email_id}")
def run_graph(email_id: int):

    return EmailProcessor.process(email_id)
