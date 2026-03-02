from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

@app.route('/download')
def download_file():
    video_url = request.args.get('url')
    download_type = request.args.get('type', 'video')
    quality = request.args.get('quality', 'best')

    if not video_url:
        return "Falta la URL del video.", 400

    try:
        ydl_opts = {
            'quiet': True,
            'ignoreerrors': True,
            'no_check_certificate': True
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
            return "No se pudo obtener un enlace de descarga para este video/calidad. Puede que no esté disponible o tenga restricciones. Prueba con otra calidad.", 404

        file_url = info.get('url')
        file_title = info.get('title', 'descarga').replace('"',"'")
        file_ext = info.get('ext', 'mp4')

        # Hacemos la petición como intermediario
        req = requests.get(file_url, stream=True)
        
        # Servimos el archivo al usuario forzando la descarga
        return Response(stream_with_context(req.iter_content(chunk_size=1024)), headers={
            'Content-Disposition': f'attachment; filename="{file_title}.{file_ext}"'
        })

    except Exception as e:
        # Esto es importante para ver los errores reales en los logs de Render
        print(f"Error procesando la descarga: {e}")
        return f"Ocurrió un error en el servidor al procesar tu solicitud.", 500
