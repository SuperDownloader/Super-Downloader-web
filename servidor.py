from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

# RUTA 1: Solo obtiene el TÍTULO y prepara los enlaces para la ruta de descarga
@app.route('/api/info')
def get_video_info():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No se proporcionó una URL"}), 400

    try:
        # Usamos una extracción rápida solo para el título
        ydl_opts = {'quiet': True, 'skip_download': True, 'ignoreerrors': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False, process=False)
        
        if info is None:
            return jsonify({"error": "No se pudo obtener información de este video.", "success": False}), 500

        response_data = {
            "success": True,
            "title": info.get('title', 'Título no disponible')
        }
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# RUTA 2: La ruta de descarga que hace de INTERMEDIARIO
@app.route('/download')
def download_file():
    video_url = request.args.get('url')
    download_type = request.args.get('type', 'video')
    quality = request.args.get('quality', 'best')

    if not video_url:
        return "Falta la URL", 400

    try:
        ydl_opts = {
            'quiet': True, 'ignoreerrors': True, 'no_check_certificate': True
        }
        
        # Lógica de selección de formato
        if download_type == 'audio':
            ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio'
        else:
            if quality == 'best':
                ydl_opts['format'] = 'best[ext=mp4]/best'
            else:
                ydl_opts['format'] = f'best[height<={quality}][ext=mp4]/best[height<={quality}]'

        # Obtenemos la información completa para la descarga
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        if info is None or not info.get('url'):
            return "No se pudo obtener un enlace de descarga para esta calidad. Prueba otra.", 404

        file_url = info.get('url')
        file_title = info.get('title', 'descarga').replace('"',"'") # Evita errores en el nombre
        file_ext = info.get('ext', 'mp4')

        # Hacemos la petición como intermediario
        req = requests.get(file_url, stream=True)
        
        # Servimos el archivo al usuario forzando la descarga
        return Response(stream_with_context(req.iter_content(chunk_size=1024)), headers={
            'Content-Disposition': f'attachment; filename="{file_title}.{file_ext}"'
        })

    except Exception as e:
        return f"Error al procesar la descarga: {e}", 500
