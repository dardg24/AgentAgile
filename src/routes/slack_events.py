import threading

from typing import Dict, Any

from flask import Blueprint, request, jsonify
from utils.funcs import is_valid_slack_request

bp_slack_events = Blueprint('slack_events', __name__)

@bp_slack_events.route('/slack/events', methods=['POST'])
def slack_events(conversation_states: Dict[str, Dict[str, Any]] = {}):
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
            thread_ts = event.get("thread_ts")
            if thread_ts and thread_ts in conversation_states:
                print(f"🔍 Respuesta detectada en hilo activo: {thread_ts}")
                text = event["text"]
                channel_id = event["channel"]
                
                # Recuperar el estado guardado
                saved_state = conversation_states[thread_ts]
                
                # Procesar con el estado previo
                threading.Thread(
                    target=process_slack_message,
                    args=(text, channel_id, thread_ts, saved_state)
                ).start()
                
                # Limpiar el estado después de usarlo (opcional)
                del conversation_states[thread_ts]
                
                return jsonify({"status": "ok"})
            
            # El resto del código existente continúa aquí...
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