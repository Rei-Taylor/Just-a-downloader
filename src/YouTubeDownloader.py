from pytubefix import YouTube
from pathlib import Path
import os
import typing as t
import subprocess
import logging
import sys

BASE_DOWNLOAD_PATH = "./downloads"
from .utils import sanitize_filename, resource_path
proxies = {"http": '88.198.212.91:3128'}
class Downloader:
    def __init__(self, url: str, output_path: str = BASE_DOWNLOAD_PATH):
        self.yt = YouTube(url=url, proxies=proxies)
        self.title = self.yt.title
        self.output = output_path
        self.thumbnail = self.yt.thumbnail_url
        self.likes = self.yt.likes
        self.views = self.yt.views
        self.videos = None
        self.audio = None 
        
        self.ensure_path()

    def ensure_path(self):
        path = Path(self.output)
        path.mkdir(parents=True, exist_ok=True)
        self.videos = path / "videos"
        self.audio = path / "audio"  
        self.videos.mkdir(exist_ok=True)
        self.audio.mkdir(exist_ok=True)  

    def get_available_resolutions(self) -> list:
        resolutions = set()
        for stream in self.yt.streams.filter(only_video=True, file_extension='mp4'):
            if stream.resolution:
                resolutions.add(stream.resolution)
        for stream in self.yt.streams.filter(progressive=True, file_extension='mp4'):
            if stream.resolution:
                resolutions.add(stream.resolution)
        
        resolution_map = {
            '4k': 2160,
            '1440p': 1440,
            '1080p': 1080,
            '720p': 720,
            '480p': 480,
            '360p': 360,
            '240p': 240,
            '144p': 144
        }
        
        def sort_key(res):
            return resolution_map.get(res.lower(), int(res.lower().replace('p', '') or 0))
        
        return sorted(resolutions, key=sort_key, reverse=True)

    def download_video(self, resolution: t.Optional[str] = None):
        try:
            safe_title = sanitize_filename(self.title)
            output_file = self.videos / f"{safe_title}_{resolution or 'highest'}.mp4"

            if not resolution:
                stream = self.yt.streams.get_highest_resolution()
            else:
                stream = self.yt.streams.filter(
                    progressive=True,
                    resolution=resolution,
                    file_extension='mp4'
                ).first()
            
            if stream:
                filename = f"{safe_title}_{resolution or 'highest'}.{stream.mime_type.split('/')[-1]}"
                stream.download(output_path=str(self.videos), filename=filename)
                print(f"Download completed (progressive): {output_file}")
                return output_file, filename

            print(f"Preparing adaptive streams for {resolution}...")
            video_stream = self.yt.streams.filter(
                only_video=True,
                resolution=resolution,
                file_extension='mp4'
            ).order_by('resolution').desc().first()
            
            audio_stream = self.yt.streams.get_audio_only()
            
            if not video_stream or not audio_stream:
                raise ValueError(f"Required streams missing for {resolution}")

            temp_video = self.videos / f"{safe_title}_temp_video.mp4"
            temp_audio = self.videos / f"{safe_title}_temp_audio.m4a" 
            
            print(f"Downloading video stream ({resolution})...")
            video_file = video_stream.download(
                output_path=str(temp_video.parent),
                filename=temp_video.name
            )
            
            print("Downloading audio stream...")
            audio_file = audio_stream.download(
                output_path=str(temp_audio.parent),
                filename=temp_audio.name
            )
            
            print("Merging streams (hardware accelerated)...")
            self.merge_video_audio_ffmpeg(video_file, audio_file, str(output_file))
            
            os.remove(video_file)
            os.remove(audio_file)
            
            print(f"Download completed (adaptive): {output_file}")
            return filename
            
        except Exception as e:
            # Attempt cleanup on failure
            for f in [temp_video, temp_audio]:
                if f.exists():
                    os.remove(f)
            raise Exception(f"Download failed: {str(e)}") from e

    def merge_video_audio_ffmpeg(self, video_path, audio_path, output_path):
        try:
            subprocess.run(
                [resource_path("ffmpeg/ffmpeg.exe"), '-version'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            logging.warning("FFmpeg not found! Falling back to slow software merge...")
            

        command = [
            f'{resource_path("ffmpeg/ffmpeg.exe")}',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',    
            '-c:a', 'copy',    
            '-map', '0:v:0', 
            '-map', '1:a:0',  
            '-y',            
            '-hide_banner',    
            '-loglevel', 'error',  
            output_path
        ]
        
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return output_path
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode().strip()
            logging.error(f"FFmpeg merge failed: {stderr}")
            

    

    def download_audio(self):
        stream = self.yt.streams.get_audio_only()
        if not stream:
            raise ValueError("No audio stream found")
        safe_title = sanitize_filename(self.title)
        stream.download(
            output_path=str(self.audio),
            filename=f"{safe_title}.m4a"  # Correct container format
        )

    def meta_data(self) -> dict:
        return {
            "title": self.title,
            "thumbnail": self.thumbnail,
            "likes": self.likes,
            "views": self.views,
            "available_resolutions": self.get_available_resolutions()
        }