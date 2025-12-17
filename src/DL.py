import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from urllib.parse import urlparse, unquote
import mimetypes
import json
from pathlib import Path

class IDMDownloader:
    def __init__(self, url, save_path=None, max_workers=8, chunk_size_mb=1, max_retries=3, output_dir="./downloads"):
        self.url = url
        self.final_url = url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.save_path = save_path
        self.max_workers = max_workers
        self.chunk_size = chunk_size_mb * 1024 * 1024
        self.max_retries = max_retries
        self.file_size = 0
        self.support_ranges = False
        self.filename = None
        self.downloaded = 0
        self.lock = Lock()
        self.chunk_status = {}
        self.start_time = None
        self.speed = 0
        
    def get_file_info(self):
        try:
            session = requests.Session()
            resp = session.head(self.url, allow_redirects=True, timeout=10)
            self.final_url = resp.url
            
            content_disp = resp.headers.get('Content-Disposition', '')
            if 'filename=' in content_disp:
                self.filename = content_disp.split('filename=')[1].strip('"\'')
            else:
                parsed = urlparse(self.final_url)
                self.filename = unquote(os.path.basename(parsed.path))
                if not self.filename:
                    content_type = resp.headers.get('Content-Type', '').split(';')[0]
                    extension = mimetypes.guess_extension(content_type) or '.bin'
                    self.filename = f"download{extension}"
            
            self.filename = self.sanitize_filename(self.filename)
            self.file_size = int(resp.headers.get('Content-Length', 0))
            self.support_ranges = resp.headers.get('Accept-Ranges', '').lower() == 'bytes'
            
            if not self.save_path:
                self.save_path = str(self.output_dir / self.filename)
            
            return {
                "filename": self.filename,
                "size_bytes": self.file_size,
                "size_mb": round(self.file_size / 1024 / 1024, 2),
                "supports_resume": self.support_ranges,
                "content_type": resp.headers.get('Content-Type', ''),
                "save_path": self.save_path
            }
            
        except Exception as e:
            print(f"Error getting file info: {e}")
            raise Exception(f"Failed to retrieve file information: {str(e)}")
    
    def sanitize_filename(self, filename):
        invalid_chars = {
            '\\': '', '/': '', ':': '', '*': '', '?': '', '"': '', 
            '<': '', '>': '', '|': '', "'": '', '™': '', '®': '', '©': ''
        }
        
        for char, replacement in invalid_chars.items():
            filename = filename.replace(char, replacement)
        
        filename = ''.join(c for c in filename if ord(c) < 128)
        
        filename = filename.strip().strip('.')
        
        max_length = 200
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length-len(ext)] + ext
        
        return filename
    
    def calculate_optimal_chunks(self):
        if not self.support_ranges or self.file_size < self.chunk_size:
            return 1
        
        if self.file_size < 10 * 1024 * 1024:  # 10MB
            return min(2, self.max_workers)
        elif self.file_size < 50 * 1024 * 1024:  # 50MB
            return min(4, self.max_workers)
        elif self.file_size < 200 * 1024 * 1024:  # 200MB
            return min(6, self.max_workers)
        else:
            return min(8, self.max_workers)
    
    def download_chunk_with_retry(self, start, end, chunk_id):
        for attempt in range(self.max_retries):
            try:
                headers = {'Range': f'bytes={start}-{end}'}
                response = requests.get(self.final_url, headers=headers, 
                                      stream=True, timeout=30)
                
                if response.status_code != 206: 
                    raise Exception(f"Server returned {response.status_code}")
                
                chunk_data = response.content
                downloaded_size = len(chunk_data)
                
                with self.lock:
                    self.downloaded += downloaded_size
                    self.chunk_status[chunk_id] = 'completed'
                    
                    with open(self.save_path, 'r+b') as f:
                        f.seek(start)
                        f.write(chunk_data)
                
                elapsed = time.time() - self.start_time
                self.speed = self.downloaded / elapsed / 1024 / 1024 if elapsed > 0 else 0 
                
                return True
                
            except Exception as e:
                print(f"\nChunk {chunk_id} attempt {attempt+1} failed: {e}")
                if attempt == self.max_retries - 1:
                    self.chunk_status[chunk_id] = 'failed'
                    return False
                time.sleep(2 ** attempt)
    
    def multi_threaded_download(self):
        num_chunks = self.calculate_optimal_chunks()
        
        if num_chunks == 1:
            yield from self.single_threaded_download()
            return
        
        with open(self.save_path, 'wb') as f:
            f.truncate(self.file_size)
        
        chunks = []
        chunk_size = self.file_size // num_chunks
        
        for i in range(num_chunks):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < num_chunks - 1 else self.file_size - 1
            chunks.append((start, end, i))
            self.chunk_status[i] = 'pending'
        
        self.start_time = time.time()
        self.downloaded = 0
        
        with ThreadPoolExecutor(max_workers=num_chunks) as executor:
            futures = []
            for start, end, chunk_id in chunks:
                future = executor.submit(
                    self.download_chunk_with_retry, 
                    start, end, chunk_id
                )
                futures.append(future)
            
            while not all(f.done() for f in futures):
                percent = (self.downloaded / self.file_size) * 100
                elapsed = time.time() - self.start_time
                remaining = (self.file_size - self.downloaded) / (self.downloaded / elapsed) if self.downloaded > 0 else 0
                self.speed = self.downloaded / elapsed / 1024 / 1024 if elapsed > 0 else 0
                
                yield {
                    "progress": round(percent, 1),
                    "downloaded_bytes": self.downloaded,
                    "speed": round(self.speed, 2),
                    "remaining_seconds": round(remaining, 1),
                    "status": "downloading"
                }
                time.sleep(0.5)
            
            all_success = True
            for future in futures:
                if not future.result():
                    all_success = False
            
            if not all_success:
                print("\nSome chunks failed, attempting recovery...")
                success = self.recover_failed_chunks(chunks)
                if not success:
                    yield {"status": "failed", "error": "Failed to recover some chunks"}
                    return
        
        actual_size = os.path.getsize(self.save_path)
        verified = actual_size == self.file_size
        
        elapsed = time.time() - self.start_time
        avg_speed = (self.file_size / 1024 / 1024) / elapsed if elapsed > 0 else 0
        
        yield {
            "status": "completed",
            "progress": 100,
            "downloaded_bytes": self.file_size,
            "speed": round(avg_speed, 2),
            "verified": verified,
            "file_path": self.save_path,
            "filename": self.filename
        }
    
    def recover_failed_chunks(self, chunks):
        print("Recovering failed chunks...")
        for start, end, chunk_id in chunks:
            if self.chunk_status.get(chunk_id) == 'failed':
                print(f"Retrying chunk {chunk_id}...")
                if not self.download_chunk_with_retry(start, end, chunk_id):
                    print(f"Chunk {chunk_id} recovery failed")
                    return False
        return True
    
    def single_threaded_download(self):
        print("Using single-threaded download...")
        try:
            response = requests.get(self.final_url, stream=True, timeout=60)
            response.raise_for_status()
            
            self.start_time = time.time()
            self.downloaded = 0
            
            with open(self.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        self.downloaded += len(chunk)
                        
                        
                        percent = (self.downloaded / self.file_size) * 100
                        elapsed = time.time() - self.start_time
                        remaining = (self.file_size - self.downloaded) / (self.downloaded / elapsed) if self.downloaded > 0 else 0
                        self.speed = self.downloaded / elapsed / 1024 / 1024 if elapsed > 0 else 0
                        
                        yield {
                            "progress": round(percent, 1),
                            "downloaded_bytes": self.downloaded,
                            "speed": round(self.speed, 2),
                            "remaining_seconds": round(remaining, 1),
                            "status": "downloading"
                        }
            
            
            actual_size = os.path.getsize(self.save_path)
            verified = actual_size == self.file_size
            
            elapsed = time.time() - self.start_time
            avg_speed = (self.file_size / 1024 / 1024) / elapsed if elapsed > 0 else 0
            
            yield {
                "status": "completed",
                "progress": 100,
                "downloaded_bytes": self.file_size,
                "speed": round(avg_speed, 2),
                "verified": verified,
                "file_path": self.save_path,
                "filename": self.filename
            }
            
        except Exception as e:
            print(f"\nDownload failed: {e}")
            yield {"status": "failed", "error": str(e)}
    
    def download(self):
        try:
            file_info = self.get_file_info()
            print(f"Starting download from: {self.url}")
            print(f"Filename: {self.filename}")
            print(f"Size: {self.file_size:,} bytes ({self.file_size/1024/1024:.2f} MB)")
            print(f"Supports resume: {self.support_ranges}")
            
            if self.support_ranges:
                yield from self.multi_threaded_download()
            else:
                yield from self.single_threaded_download()
                
        except Exception as e:
            print(f"Download error: {e}")
            yield {"status": "failed", "error": str(e)}