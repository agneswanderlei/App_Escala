import requests
from dotenv import load_dotenv
import os
from pathlib import Path

# Força o caminho absoluto para o .env na raiz
env_path = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(env_path)
EVOLUTION_AUTHENTICATION_API_KEY = os.getenv('AUTHENTICATION_API_KEY')

def send_whatsapp_message(number: str, text: str, instance_name: str):
    """
    Envia uma mensagem de texto via WhatsApp.
    O nome da instância é passado dinamicamente.
    """
    url = f'http://72.60.155.96:8080/message/sendText/{instance_name}'
    headers = {
        'apikey': EVOLUTION_AUTHENTICATION_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        'number': number,
        'text': text,
    }
    response = requests.post(
        url=url,
        json=payload,
        headers=headers
    )
    return response.json()