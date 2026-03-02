# (Todas las importaciones de antes se mantienen)
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

@app.route('/api/info')
def get_video_info():
    video_url = request.args.get('url')
    # NUEVOS PARÁMETROS
    download_type = request.args.get('type', 'video')
    quality = request.args.get('quality', 'best')

    if not video_url:
        return jsonify({"error": "No se proporcionó una URL"}), 400

    try:
        ydl_opts = {
            'quiet': True, 'skip_download': True, 'ignoreerrors': True,
            'no_check_certificate': True,
        }

        # Lógica para seleccionar el formato correcto
        format_selector = ""
        if download_type == 'audio':
            format_selector = 'bestaudio[ext=m4a]/bestaudio'
        else: # video
            # Buscamos un formato pre-fusionado (evita necesitar FFmpeg)
            if quality == 'best':
                format_selector = 'best[ext=mp4]/best'
            else:
                format_selector = f'best[height<={quality}][ext=mp4]/best[height<={quality}]'
        
        ydl_opts['format'] = format_selector

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
        
        if info is None or not info.get('url'):
            return jsonify({"error": "No se pudo obtener un enlace de descarga para este video y calidad. Prueba con otra calidad (ej. 360p).", "success": False}), 500
            
        # El título y la URL del video para el botón de descarga
        response_data = {
            "success": True,
            "title": info.get('title', 'Título no disponible'),
            "download_url": info.get('url'),
            "filename": f"{info.get('title', 'video')}.{info.get('ext', 'mp4')}"
        }
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# La ruta /download ya no es necesaria, todo se hace en /api/info
# Podemos borrarla o dejarla por si acaso, pero ya no la usaremos.
