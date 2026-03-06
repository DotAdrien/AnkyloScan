import requests

# Remplace par tes valeurs ⚙️
SERVER_IP = "{SERVER_IP}"
TOKEN = "{TOKEN}" 
URL = f"http://{SERVER_IP}:8001/logs/ingest"

def send_log(event_id, source, message):
    data = {
        "token": TOKEN,
        "event_id": event_id,
        "source": source,
        "message": message
    }
    try:
        response = requests.post(URL, json=data)
        print(f"Statut : {response.status_code} ✨")
    except Exception as e:
        print(f"Erreur envoi log : {e} 😱")

# Exemple d'appel 🛡️
send_log(1, "Agent-007", "Scan détecté avec succès ! 👍")