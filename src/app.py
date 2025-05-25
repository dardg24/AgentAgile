import threading

from core import process_slack_message
from utils import is_valid_slack_request
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    """Manejador principal para eventos de Slack."""
    if not is_valid_slack_request():
        return jsonify({'error': 'invalid_request'}), 403
    
    data = request.json
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})
    
    # Procesar eventos
    if "event" in data:
        event = data["event"]
        
        # Solo procesar mensajes que no sean del propio bot
        if "bot_id" not in event:
            if event["type"] == "app_mention":
                # Extraer el mensaje sin la mención del bot
                text = event["text"].split(">", 1)[1].strip()
                channel_id = event["channel"]
                
                # Procesar el mensaje en un hilo separado
                threading.Thread(
                    target=process_slack_message,
                    args=(text, channel_id)
                ).start()
                
            elif event["type"] == "message" and "channel" in event:
                text = event["text"]
                channel_id = event["channel"]
                
                # Procesar solo mensajes con prefijo "trello:"
                if text.lower().startswith("trello:"):
                    text = text[7:].strip()  
                    threading.Thread(
                        target=process_slack_message,
                        args=(text, channel_id)
                    ).start()
    
    # Slack requiere una respuesta rápida
    return jsonify({"status": "ok"})

@app.route('/slack/interactive', methods=['POST'])
def slack_interactive():
    """Maneja las interacciones con botones y otros elementos interactivos."""
    if not is_valid_slack_request():
        return jsonify({'error': 'invalid_request'}), 403
    
    # Por ahora, simplemente responder OK a cualquier interacción
    # En futuras versiones, aquí se puede delegar al agente
    return "", 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=3000)