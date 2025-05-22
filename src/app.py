import json
import threading

from typing import Dict, Any

from core.agent import process_slack_message
from utils.funcs import is_valid_slack_request
from flask import Flask, request, jsonify
from core.tools import (
    send_to_slack, 
    get_trello_lists,
    move_card_between_lists
)
from utils.config import BOARD_ID

conversation_states: Dict[str, Dict[str, Any]] = {}

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

@app.route('/slack/interactive', methods=['POST'])
def slack_interactive():
    """Maneja las interacciones con botones y otros elementos interactivos."""
    if not is_valid_slack_request():
        return jsonify({'error': 'invalid_request'}), 403
    
    try:
        # Los datos de interactividad vienen como form-data
        form_data = request.form
        payload_str = form_data.get('payload', '{}')
        
        payload = json.loads(payload_str)
        
        # Extraer información relevante
        action_type = payload.get('type')
        
        if action_type == 'block_actions':
            # Obtener detalles de la acción
            actions = payload.get('actions', [])
            if not actions:
                return "", 200
                
            action = actions[0]
            value = action.get('value', '')
            
            # Obtener información de contexto
            channel_id = payload.get('channel', {}).get('id')
            user_id = payload.get('user', {}).get('id')
            thread_ts = payload.get('message', {}).get('ts')
            
            # PROCESAMIENTO DE BOTONES CON JSON
            try:
                # Intentar cargar el valor como JSON
                button_data = json.loads(value)
                action_name = button_data.get('action')
                
                if action_name == 'create_card':
                    list_name = button_data.get('list_name')
                    prompt = f"What would you like to name the new card in '{list_name}'?"
                    blocks = [{
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": prompt
                        }
                    }]

                    slack_response = send_to_slack(prompt, channel_id, blocks=blocks, thread_ts=thread_ts)

                    message_ts = thread_ts if thread_ts else slack_response.get("ts", "")

                    # Guardar el estado para esta conversación
                    conversation_states[message_ts] = {
                        "channel_id": channel_id,
                        "conversation_state": "awaiting_card_name",
                        "conversation_context": {
                            "list_name": list_name,
                            "action": "create_card"
                        },
                        "thread_ts": message_ts
                    }
                    print(f"💾 Estado guardado para thread {message_ts}: {conversation_states[message_ts]}")
                
                elif action_name == 'move_card':
                    source_list = button_data.get('source_list')
                    card_name = button_data.get('card_name')
                    
                    # Obtener listas para mostrar opciones
                    lists = get_trello_lists(BOARD_ID)
                    if not lists:
                        send_to_slack("Sorry, I couldn't retrieve the lists from your board.", 
                                     channel_id, thread_ts=thread_ts)
                        return "", 200
                    
                    # Crear mensaje con opciones de destino
                    blocks = [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"Where would you like to move the card *{card_name}*?"
                            }
                        },
                        {
                            "type": "actions",
                            "elements": []
                        }
                    ]
                    
                    # Añadir cada lista como botón
                    for list_name in lists.keys():
                        if list_name != source_list:  # Excluir la lista actual
                            blocks[1]["elements"].append({
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": list_name,
                                    "emoji": True
                                },
                                "value": json.dumps({
                                    "action": "move_confirm",
                                    "source_list": source_list,
                                    "card_name": card_name,
                                    "target_list": list_name
                                })
                            })
                    
                    send_to_slack("Select destination list", channel_id, blocks=blocks, thread_ts=thread_ts)
                
                elif action_name == 'move_confirm':
                    source_list = button_data.get('source_list')
                    card_name = button_data.get('card_name')
                    target_list = button_data.get('target_list')
                    
                    # Mover la tarjeta y notificar el resultado
                    result = move_card_between_lists(
                        card_name=card_name,
                        source_list_name=source_list,
                        target_list_name=target_list,
                        board_id=BOARD_ID,
                        channel_id=channel_id
                    )
                
            except json.JSONDecodeError as e:
                print(f"Error decodificando JSON: {str(e)}")
            
            except Exception as e:
                send_to_slack(f"Sorry, I encountered an error: {str(e)}", 
                             channel_id, thread_ts=thread_ts)
    
    except Exception as e:
        pass
    
    # Slack necesita una respuesta rápida
    return "", 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=3000)