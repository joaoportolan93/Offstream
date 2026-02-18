"""
Offstream Mobile - Módulo de Download
Lógica reutilizável para download de vídeos/áudios
"""
import os
import threading
from yt_dlp import YoutubeDL


# Logger nulo para suprimir saída do yt-dlp
class NullLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass
    def info(self, msg): pass


class MediaDownloader:
    """Classe para gerenciar downloads de mídia"""
    
    def __init__(self, download_dir=None):
        self.download_dir = download_dir or os.path.join(os.path.expanduser("~"), "Downloads")
        self.current_download = None
        self.cancelled = False
        self.progress_callback = None
        self.complete_callback = None
        self.error_callback = None
        self.info_callback = None
    
    def set_download_dir(self, path):
        """Define diretório de download"""
        self.download_dir = path
    
    def get_video_info(self, url, callback=None):
        """Obtém informações do vídeo em background"""
        def fetch():
            try:
                opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'logger': NullLogger(),
                    'extract_flat': False,
                }
                with YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if callback:
                        callback({
                            'title': info.get('title', 'Sem título'),
                            'duration': info.get('duration', 0) or 0,
                            'thumbnail': info.get('thumbnail', ''),
                            'uploader': info.get('uploader', 'Desconhecido'),
                        })
            except Exception as e:
                if self.error_callback:
                    self.error_callback(str(e))
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def download(self, url, format_type='mp4', quality='720'):
        """Inicia download em background"""
        self.cancelled = False
        
        def do_download():
            try:
                ydl_opts = self._get_options(format_type, quality)
                
                with YoutubeDL(ydl_opts) as ydl:
                    self.current_download = ydl
                    if not self.cancelled:
                        ydl.download([url])
                
                if not self.cancelled and self.complete_callback:
                    self.complete_callback()
                    
            except Exception as e:
                if self.error_callback:
                    self.error_callback(str(e))
            finally:
                self.current_download = None
        
        threading.Thread(target=do_download, daemon=True).start()
    
    def cancel(self):
        """Cancela download atual"""
        self.cancelled = True
    
    def _progress_hook(self, d):
        """Hook para progresso do download"""
        if self.cancelled:
            return
            
        if d['status'] == 'downloading':
            try:
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                
                if total > 0:
                    percent = (downloaded / total) * 100
                    speed = d.get('speed', 0) or 0
                    speed_mb = speed / 1024 / 1024
                    
                    if self.progress_callback:
                        self.progress_callback(percent, f"{speed_mb:.1f} MB/s")
            except:
                pass
    
    def _get_options(self, format_type, quality):
        """Retorna opções do yt-dlp baseado no formato"""
        base_opts = {
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'logger': NullLogger(),
        }
        
        if format_type == 'mp3':
            return {
                **base_opts,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
            }
        else:  # mp4
            return {
                **base_opts,
                'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best',
                'merge_output_format': 'mp4',
            }
