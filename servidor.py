from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import time

app = Flask(__name__)
CORS(app)

@app.route('/get_manifest')
def get_manifest():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No se proporcionó una URL"}), 400

    # Aumentamos la "paciencia" con reintentos
    for i in range(3): # Intentaremos hasta 3 veces
        try:
            ydl_opts = {
                'quiet': True,
                'ignoreerrors': True,
                'no_check_certificate': True,
                # Forzar la extracción del manifiesto
                'extract_flat': 'in_playlist',
                'dump_single_json': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

            if info is None:
                raise ValueError("yt-dlp no devolvió información.")

            # Buscamos un manifiesto HLS o DASH de la información extraída
            manifest_url = None
            title = info.get('title', 'Video')
            
            # Buscamos en la lista de formatos
            for f in info.get('formats', []):
                if f.get('protocol') == 'm3u8_native' or f.get('protocol') == 'm3u8':
                    manifest_url = f.get('url')
                    break 
                elif f.get('protocol') == 'mpd':
                    manifest_url = f.get('url')
            
            if not manifest_url:
                 if info.get('url'):
                    return jsonify({ "manifest_url": info.get('url'), "title": title, "is_direct": True })
                 else:
                    raise ValueError("No se encontró un manifiesto o enlace de video compatible.")

            # Si llegamos aquí, tuvimos éxito
            return jsonify({ "manifest_url": manifest_url, "title": title, "is_direct": False })
        
        except Exception as e:
            # Si fallamos, lo registramos, esperamos un segundo y lo reintentamos
            print(f"Intento {i+1} fallido: {e}")
            if i < 2: # Si no es el último intento
                time.sleep(1)
            else: # Si es el último intento, devolvemos el error
                return jsonify({"error": f"El servidor no pudo procesar la URL después de varios intentos. Error: {e}"}), 500
