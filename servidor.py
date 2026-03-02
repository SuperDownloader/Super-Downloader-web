from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- 1. IMPORTAMOS LA NUEVA LIBRERÍA
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # <-- 2. APLICAMOS EL "PERMISO ESPECIAL" A TODA NUESTRA APP

@app.route('/api/info')
def get_video_info():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No se proporcionó una URL"}), 400

    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
        
        formats = info.get('formats', [])
        
        video_link = None
        for f in formats:
            if f.get('ext') == 'mp4' and f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                video_link = f.get('url')
                break

        audio_link = None
        for f in formats:
            if f.get('ext') == 'm4a' or (f.get('acodec') != 'none' and f.get('vcodec') == 'none'):
                audio_link = f.get('url')
                break

        response_data = {
            "success": True,
            "title": info.get('title', 'Título no disponible'),
            "thumbnail": info.get('thumbnail', ''),
            "links": {
                "video": video_link,
                "audio": audio_link
            }
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500
