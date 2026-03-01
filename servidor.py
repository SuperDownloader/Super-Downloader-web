from flask import Flask, request, jsonify
import yt_dlp

# Creamos la aplicación Flask
app = Flask(__name__)

@app.route('/api/info')
def get_video_info():
    # 1. Obtenemos la URL que nos envían desde la página web
    video_url = request.args.get('url')

    # Si no nos envían una URL, devolvemos un error
    if not video_url:
        return jsonify({"error": "No se proporcionó una URL"}), 400

    try:
        # 2. Usamos yt-dlp para EXTRAER INFORMACIÓN, NO para descargar aún.
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        # 3. Buscamos los formatos que nos interesan
        formats = info.get('formats', [])
        
        # Buscamos el mejor video MP4 (que ya contenga audio)
        video_link = None
        for f in formats:
            if f.get('ext') == 'mp4' and f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                video_link = f.get('url')
                break 

        # Buscamos el mejor audio M4A
        audio_link = None
        for f in formats:
            if f.get('ext') == 'm4a' or (f.get('acodec') != 'none' and f.get('vcodec') == 'none'):
                audio_link = f.get('url')
                break

        # 4. Preparamos una respuesta bonita en formato JSON
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
        # Si algo sale mal, informamos del error
        return jsonify({"error": str(e), "success": False}), 500

# Esto es para poder ejecutarlo directamente
if __name__ == '__main__':
    app.run(debug=True, port=5001)