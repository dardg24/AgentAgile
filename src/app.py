from flask import Flask, request, jsonify
import threading
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# Importar componentes existentes del agente
# Asumiendo que tienes un archivo agent.py con tu implementación de LangGraph
from agent import process_slack_message

app = Flask(__name__)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    # Verificar que la solicitud proviene de Slack
    # Esto debería implementarse para producción
    
    data = request.json
    
    # Manejar la verificación de URL de Slack
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
                
                # Procesar el mensaje en un hilo separado para no bloquear la respuesta a Slack
                threading.Thread(
                    target=process_slack_message,
                    args=(text, channel_id)
                ).start()
                
            elif event["type"] == "message" and "channel" in event:
                # Puedes procesar todos los mensajes o solo en canales específicos
                # Comenta esto si solo quieres responder a menciones
                text = event["text"]
                channel_id = event["channel"]
                
                # Procesar solo mensajes que contengan una palabra clave, por ejemplo "trello:"
                if text.lower().startswith("trello:"):
                    text = text[7:].strip()  # Remover "trello:"
                    threading.Thread(
                        target=process_slack_message,
                        args=(text, channel_id)
                    ).start()
    
    # Slack requiere una respuesta rápida
    return jsonify({"status": "ok"})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=3000)