from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/get_manifest')
def get_manifest():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No se proporcionó una URL"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'ignoreerrors': True,
            'no_check_certificate': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        if info is None:
            return jsonify({"error": "yt-dlp no pudo procesar esta URL."}), 500

        # Buscamos un manifiesto HLS o DASH
        manifest_url = None
        title = info.get('title', 'Video')
        
        for f in info.get('formats', []):
            if f.get('protocol') == 'm3u8_native' or f.get('protocol') == 'm3u8':
                manifest_url = f.get('url')
                break # Preferimos HLS si está disponible
            elif f.get('protocol') == 'mpd':
                manifest_url = f.get('url')
        
        if not manifest_url:
             # Plan B: Si no hay manifiesto, buscar un enlace directo
            if info.get('url'):
                return jsonify({ "manifest_url": info.get('url'), "title": title, "is_direct": True })
            else:
                return jsonify({"error": "No se encontró un manifiesto o enlace de video compatible."}), 404

        return jsonify({ "manifest_url": manifest_url, "title": title, "is_direct": False })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
