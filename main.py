import os
import threading
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from pathlib import Path
import typing as t
import webview
from downloader import Downloader



app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class UrlRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    resolution: t.Optional[str] = None

@app.post("/api/metadata")
async def get_metadata(request: UrlRequest):
    try:
        downloader = Downloader(request.url)
        return downloader.meta_data()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/download/video")
async def download_video(request: DownloadRequest):
    try:
        downloader = Downloader(request.url)
        downloader.download_video(request.resolution)
        return {"success": True, "message": f"Video downloaded to {downloader.videos}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/download/audio")
async def download_audio(request: DownloadRequest):
    try:
        downloader = Downloader(request.url)
        downloader.download_audio()
        return {"success": True, "message": f"Audio downloaded to {downloader.Audio}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    # Start FastAPI server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    import time
    time.sleep(1)
    
    # Create pywebview window
    window = webview.create_window(
        "YouTube Downloader",
        "http://127.0.0.1:8000",
        width=800,
        height=600,
        resizable=True
    )
    webview.start()