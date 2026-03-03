from flask import Flask, request, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/proxy')
def proxy_request():
    # Obtenemos la URL que el frontend quiere visitar
    target_url = request.args.get('url')
    if not target_url:
        return "Falta la URL de destino.", 400
    
    try:
        # Hacemos la petición como si fuéramos un navegador normal
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(target_url, headers=headers)
        
        # Devolvemos el contenido de la página tal cual al frontend
        return Response(response.content, content_type=response.headers['Content-Type'])
        
    except Exception as e:
        return f"Error en el proxy: {e}", 500
