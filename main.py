import os, json, asyncio
import threading, uuid
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from pathlib import Path
import typing as t
import webview
from src.YouTubeDownloader import Downloader

from src.DL import IDMDownloader
from src.utils import sanitize_filename, resource_path
from fastapi.responses import StreamingResponse


BASE_DOWNLOAD_PATH = "./downloads"
app = FastAPI()
templates = Jinja2Templates(directory=resource_path("templates"))
static_path = resource_path("static")
app.mount("/static", StaticFiles(directory=static_path), name="static")



class UrlRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    resolution: t.Optional[str] = None

class FileRequest(BaseModel):
    url: str
    max_workers: int = 8
    chunk_size_mb: int = 1    

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
    
@app.post("/api/file/info")
async def get_file_info(request: FileRequest):
    try:
        print(request)
        downloader = IDMDownloader(
            url=request.url,
            max_workers=request.max_workers,
            chunk_size_mb=request.chunk_size_mb
        )
        info = downloader.get_file_info()
        
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

active_downloads = {}

@app.post("/api/file/download")
async def download_file(request: FileRequest):
    try:
        def generator():
            downloader = IDMDownloader(
                url=request.url,
                max_workers=request.max_workers,
                chunk_size_mb=request.chunk_size_mb,
                output_dir=BASE_DOWNLOAD_PATH
            )
            
            for progress in downloader.download():
                yield f"data: {json.dumps(progress)}\n\n"
        
        return StreamingResponse(generator(), media_type="text/event-stream")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/file/download/progress")
async def download_progress(download_id: str):
    if download_id not in active_downloads:
        raise HTTPException(status_code=404, detail="Download ID not found")
    
    download_info = active_downloads[download_id]
    
    async def event_generator():
        downloader = IDMDownloader(
            url=download_info["url"],
            max_workers=download_info["max_workers"],
            chunk_size_mb=download_info["chunk_size_mb"],
            
        )
        
        for progress in downloader.download():
            yield f"data: {json.dumps(progress)}\n\n"
            await asyncio.sleep(0.1)
        
        if download_id in active_downloads:
            del active_downloads[download_id]
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    import time, sys
    time.sleep(1)
    
    sys.stdout = open("log.txt", "w")
    window = webview.create_window(
        "YouTube Downloader",
        "http://127.0.0.1:8000",
        width=800,
        height=600,
        resizable=True
    )
    webview.start()