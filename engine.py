# engine.py
import yt_dlp
import os

class VideoDownloader:
    def __init__(self, custom_ffmpeg_path=None):
        # 1. Rutas
        self.default_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        
        # Detectar ruta pública Android
        if os.path.exists("/storage/emulated/0/Download"):
            self.default_path = "/storage/emulated/0/Download"

    def download(self, url, path, format_ext, resolution, progress_hook):
        if not path:
            path = self.default_path
            
        # Forzar ruta Android pública
        if "/storage/emulated/0" not in path and os.path.exists("/storage/emulated/0/Download"):
            path = "/storage/emulated/0/Download"

        # --- DETECCIÓN DE ENTORNO ---
        # En PC (Windows) buscamos el .exe
        is_windows = os.name == 'nt'
        has_ffmpeg = is_windows and os.path.exists("ffmpeg.exe")

        # --- CONFIGURACIÓN BASE ---
        ydl_opts = {
            'outtmpl': f'{path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'quiet': False,
            'ignoreerrors': False,
            'overwrites': True,
            'http_headers': {'User-Agent': 'Mozilla/5.0...'},
            # Desactivamos subtítulos
            'writesubtitles': False,
            'writeautomaticsub': False,
            'embedsubtitles': False,
            # CRÍTICO: Desactivar FFmpeg explícitamente en Android
            'ffmpeg_location': None, 
        }

        # Si estamos en PC, activamos FFmpeg
        if has_ffmpeg:
            ydl_opts['ffmpeg_location'] = os.path.abspath("ffmpeg.exe")

        is_audio = format_ext in ['mp3', 'wav', 'aiff']

        # --- LÓGICA DE FORMATOS ---
        
        if is_audio:
            if has_ffmpeg:
                # PC: Convertimos a MP3
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format_ext,
                    'preferredquality': '192',
                }]
            else:
                # ANDROID: M4A DIRECTO.
                # 'bestaudio[ext=m4a]' busca el audio AAC nativo.
                # NO usamos postprocessors.
                print("Modo Android: Audio Nativo M4A")
                ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio'
        else:
            # VIDEO
            if has_ffmpeg:
                # PC: Calidad máxima (Unión)
                if resolution == 'best':
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
                else:
                    ydl_opts['format'] = f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]'
                ydl_opts['merge_output_format'] = format_ext
            else:
                # ANDROID: Archivo único obligatorio.
                # Usamos 'best[ext=mp4]' para forzar un archivo que ya tenga video y audio.
                # Esto evita el error "merging of multiple formats".
                print("Modo Android: Video Único (MP4)")
                
                if resolution == 'best':
                     ydl_opts['format'] = 'best[ext=mp4]/best'
                else:
                     # Intentamos buscar mp4 directo de esa resolución
                     ydl_opts['format'] = f'best[height<={resolution}][ext=mp4]/best[height<={resolution}][ext=mp4]/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            msg = "¡Descarga Exitosa!"
            if not has_ffmpeg and is_audio:
                msg = "Guardado como M4A (Compatible)"
            
            return True, msg
            
        except Exception as e:
            return False, f"Error: {str(e)}"