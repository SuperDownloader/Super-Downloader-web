from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import requests # <-- Importamos la nueva librería

app = Flask(__name__)
CORS(app)

# --- RUTA 1: OBTENER INFORMACIÓN (como antes) ---
@app.route('/api/info')
def get_video_info():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No se proporcionó una URL"}), 400

    try:
        ydl_opts = {
            'quiet': True, 'skip_download': True, 'ignoreerrors': True,
            'no_check_certificate': True, 'youtube_include_dash_manifest': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
        
        if info is None:
            return jsonify({"error": "No se pudo obtener información de este video. Puede que sea privado o tenga restricciones.", "success": False}), 500

        formats = info.get('formats', [])
        
        video_format = None
        for f in formats:
            if f.get('ext') == 'mp4' and f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                video_format = f
                break

        audio_format = None
        for f in formats:
            if f.get('ext') == 'm4a' or (f.get('acodec') != 'none' and f.get('vcodec') == 'none'):
                audio_format = f
                break

        response_data = {
            "success": True,
            "title": info.get('title', 'Título no disponible'),
            "thumbnail": info.get('thumbnail', ''),
            "links": {
                # Ya no pasamos el link directo, pasamos la URL del video original
                "video": video_url if video_format else None,
                "audio": video_url if audio_format else None,
            }
        }
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# --- RUTA 2: LA NUEVA RUTA DE DESCARGA ---
@app.route('/download')
def download_file():
    video_url = request.args.get('url')
    download_type = request.args.get('type', 'video') # 'video' o 'audio'

    if not video_url:
        return "Falta la URL", 400

    try:
        # Volvemos a extraer la info para tener los enlaces frescos
        ydl_opts = {'quiet': True, 'skip_download': True, 'ignoreerrors': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        # Seleccionamos el formato correcto
        target_format = None
        if download_type == 'video':
            for f in info['formats']:
                if f.get('ext') == 'mp4' and f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    target_format = f
                    break
        else: # audio
            for f in info['formats']:
                if f.get('ext') == 'm4a' or (f.get('acodec') != 'none' and f.get('vcodec') == 'none'):
                    target_format = f
                    break
        
        if not target_format:
            return "No se encontró un formato de descarga válido.", 404

        file_url = target_format['url']
        file_title = info.get('title', 'descarga')
        file_ext = target_format.get('ext', 'mp4' if download_type == 'video' else 'm4a')
        
        # Hacemos de intermediario (proxy)
        req = requests.get(file_url, stream=True)
        return Response(stream_with_context(req.iter_content(chunk_size=1024)), headers={
            'Content-Disposition': f'attachment; filename="{file_title}.{file_ext}"'
        })

    except Exception as e:
        return f"Error al procesar la descarga: {e}", 500
