from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.websocket import router as websocket_router

app = FastAPI(
    title="Connectify",
    description="A real-time chat application built with FastAPI and WebSockets.",
    version="0.1.0",
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files ---
# Determine the base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
# Ensure the static directory exists
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Serve the index.html file directly
    html_file_path = os.path.join(static_dir, "index.html")
    if os.path.exists(html_file_path):
        with open(html_file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    else:
        return HTMLResponse(
            content="<h1>Chat App</h1><p>Frontend not found. Please create static/index.html</p>",
            status_code=404,
        )


# Include the WebSocket router
app.include_router(websocket_router)


# --- Health Check ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}
