from flask import Flask, request, jsonify
import threading
import json
from agent import process_slack_message

app = Flask(__name__)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    # Verificar token de seguridad
    data = request.json
    
    # Lógica para manejar diferentes tipos de eventos
    if 'challenge' in data:
        # Respuesta para el desafío de verificación de URL
        return jsonify({"challenge": data["challenge"]})
    
    # Procesamiento de mensajes
    if 'event' in data and data['event']['type'] == 'message':
        # Extraer información relevante
        channel_id = data['event']['channel']
        user_message = data['event']['text']
        
        # Procesar asíncronamente para evitar timeout
        threading.Thread(target=process_slack_message, 
                        args=(user_message, channel_id)).start()
    
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)