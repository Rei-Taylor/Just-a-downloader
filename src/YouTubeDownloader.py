from moviepy.editor import VideoFileClip, AudioFileClip
from pytubefix import YouTube
from pathlib import Path
import os
import typing as t
BASE_DOWNLOAD_PATH = "./downloads"
from .utils import sanitize_filename

class Downloader:
    def __init__(self, url: str, output_path: str = BASE_DOWNLOAD_PATH):
        self.yt = YouTube(url=url)
        self.title = self.yt.title
        self.output = output_path
        self.thumbnail = self.yt.thumbnail_url
        self.likes = self.yt.likes
        self.views = self.yt.views
        self.videos = None
        self.Audio = None
        self.ensure_path()

    def ensure_path(self):
        path = Path(self.output)
        path.mkdir(parents=True, exist_ok=True)
        self.videos = path / "videos"
        self.Audio = path / "audio"
        self.videos.mkdir(exist_ok=True)
        self.Audio.mkdir(exist_ok=True)

    
    def get_available_resolutions(self) -> list:
        resolutions = set()
        for stream in self.yt.streams.filter(only_video=True):
            if stream.resolution:
                resolutions.add(stream.resolution)
        for stream in self.yt.streams.filter(progressive=True):
            if stream.resolution:
                resolutions.add(stream.resolution)
        
        sorted_resolutions = sorted(
            resolutions, 
            key=lambda x: int(x.replace('p', '').replace('4k', '2160'))
        )
        return sorted_resolutions

    def download_video(self, resolution: t.Optional[str] = None):
        try:
            if resolution:
                video_stream = self.yt.streams.filter(
                    only_video=True, 
                    resolution=resolution,
                    file_extension='mp4'
                ).first()
                
                if video_stream:
                    audio_stream = self.yt.streams.get_audio_only()
                    if not audio_stream:
                        raise ValueError("No audio stream available")
                    
                    safe_title = sanitize_filename(self.title)
                    temp_video = self.videos / f"{safe_title}_temp_video.mp4"
                    temp_audio = self.videos / f"{safe_title}_temp_audio.mp3"
                    output_file = self.videos / f"{safe_title}_{resolution}.mp4"
                    
                    print(f"Downloading video stream ({resolution})...")
                    video_file = video_stream.download(output_path=str(temp_video.parent), filename=temp_video.name)
                    
                    print("Downloading audio stream...")
                    audio_file = audio_stream.download(output_path=str(temp_audio.parent), filename=temp_audio.name)
                    
                    print("Merging video and audio streams...")
                    self.merge_video_audio(video_file, audio_file, str(output_file))
                    
                    os.remove(video_file)
                    os.remove(audio_file)
                    
                    print(f"Download completed: {output_file}")
                    return
            
            if not resolution:
                stream = self.yt.streams.get_highest_resolution()
            else:
                stream = self.yt.streams.filter(progressive=True, resolution=resolution).first()
            
            if not stream:
                stream = self.yt.streams.filter(resolution=resolution).first()
                if not stream:
                    raise ValueError(f"No stream found for resolution: {resolution}")
            
            safe_title = self.sanitize_filename(self.title)
            if resolution:
                filename = f"{safe_title}_{resolution}.{stream.mime_type.split('/')[-1]}"
            else:
                filename = f"{safe_title}.{stream.mime_type.split('/')[-1]}"
            
            stream.download(output_path=str(self.videos), filename=filename)
            
        except Exception as e:
            raise Exception(f"Error downloading video: {str(e)}")

    def merge_video_audio(self, video_path, audio_path, output_path):
        try:
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            
            final_clip = video_clip.set_audio(audio_clip)
            
            final_clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                threads=4,
                logger=None 
            )
            
            video_clip.close()
            audio_clip.close()
            final_clip.close()
            
            return str(output_path)
        except Exception as e:
            import logging
            logging.error(f"{e}")
            raise Exception(f"Error merging video and audio: {str(e)}")

    def download_audio(self):
        stream = self.yt.streams.get_audio_only()
        if not stream:
            raise ValueError("No audio stream found")
        stream.download(output_path=self.Audio, filename=f"{self.title}.mp3")

    def meta_data(self) -> dict:
        return {
            "title": self.title,
            "thumbnail": self.thumbnail,
            "likes": self.likes,
            "views": self.views,
            "available_resolutions": self.get_available_resolutions()
        }
    
    