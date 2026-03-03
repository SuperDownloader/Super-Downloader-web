from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app) # Habilitamos CORS para que CodePen pueda hablar con nosotros

@app.route('/get_video_link')
def get_video_link():
    # Obtenemos la URL que nos manda el frontend
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No se proporcionó una URL"}), 400

    try:
        # La URL de la API de Cobalt
        cobalt_api_url = 'https://co.wuk.sh/api/json'
        
        # El cuerpo de la petición que le enviaremos a Cobalt
        payload = {
            "url": video_url,
            "vQuality": "720",
            "isNoTTWatermark": True
        }

        # Nuestro servidor hace la petición POST a Cobalt
        response = requests.post(cobalt_api_url, json=payload, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Verificamos que la respuesta de Cobalt sea exitosa
        response.raise_for_status() # Esto lanzará un error si la respuesta es 4xx o 5xx
        
        # Devolvemos la respuesta JSON de Cobalt directamente a nuestro frontend
        return jsonify(response.json())

    except requests.exceptions.RequestException as e:
        # Si hay un error de red al contactar a Cobalt
        return jsonify({"error": f"Error al contactar la API externa: {e}"}), 502
    except Exception as e:
        # Para cualquier otro error
        return jsonify({"error": f"Ocurrió un error inesperado en el servidor: {e}"}), 500
