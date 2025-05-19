import hmac
import hashlib
import time
import os

from flask import request


# Cargado de tu variable de entorno
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")


def is_valid_slack_request():
    # 1. Obtener la marca de tiempo y la firma de los encabezados
    timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    slack_signature = request.headers.get('X-Slack-Signature', '')
    
    # 2. Verificar que la solicitud no sea demasiado antigua (previene ataques de repetición)
    # Si la solicitud tiene más de 5 minutos, rechazarla
    current_timestamp = int(time.time())
    if abs(current_timestamp - int(timestamp)) > 300:
        return False
    
    # 3. Reconstruir la cadena base que Slack usó para generar la firma
    request_body = request.get_data().decode('utf-8')
    base_string = f"v0:{timestamp}:{request_body}"
    
    # 4. Calcular el hash HMAC-SHA256 usando tu signing secret
    signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode('utf-8'),
        base_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # 5. Comparar tu firma calculada con la proporcionada por Slack
    return hmac.compare_digest(signature, slack_signature)