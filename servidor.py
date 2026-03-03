from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/get_fragments')
def get_fragments():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No se proporcionó una URL"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'ignoreerrors': True,
            'no_check_certificate': True,
            # Pedimos un formato que venga en fragmentos (DASH para MP4)
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        if info is None:
            return jsonify({"error": "No se pudo obtener información del video."}), 500

        # Buscamos el formato que tiene la lista de fragmentos
        video_format = None
        for f in info.get('formats', []):
            if f.get('fragments'):
                 video_format = f
                 break
        
        if not video_format:
            # Si no hay fragmentos, ofrecemos una descarga directa como Plan B
            return jsonify({
                "title": info.get('title', 'video'),
                "filename": f"{info.get('title', 'video')}.{info.get('ext', 'mp4')}",
                "is_direct": True,
                "url": info.get('url')
            })

        # Extraemos las URLs de los fragmentos
        fragments = [frag['url'] for frag in video_format.get('fragments', [])]

        return jsonify({
            "title": info.get('title', 'video'),
            "filename": f"{info.get('title', 'video')}.mp4",
            "is_direct": False,
            "fragments": fragments
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
