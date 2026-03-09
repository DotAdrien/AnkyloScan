from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import subprocess
import os

app = FastAPI()

@app.post("/build")
async def build_agent(request: Request):
    data = await request.json()
    ip = data.get("ip", "127.0.0.1")
    token = data.get("token", "default")
    
    # Code de l'agent avec IP et Token dynamiques 🤖
    agent_code = f"""import requests
SERVER_IP = "{ip}"
TOKEN = "{token}" 
URL = f"http://{{SERVER_IP}}:8001/logs/ingest"

def send_log(event_id, source, message):
    data = {{
        "token": TOKEN,
        "event_id": event_id,
        "source": source,
        "message": message
    }}
    try:
        requests.post(URL, json=data)
    except:
        pass

send_log(1, "Agent", "Agent démarré avec succès ! 👍")
"""
    
    # On sauvegarde le script 💾
    with open("agent.py", "w") as f:
        f.write(agent_code)
        
    # Compilation 🥵
    subprocess.run(["pyinstaller", "--onefile", "agent.py"], check=False)
    
    # PyInstaller sous Linux crée un binaire sans extension. On s'assure qu'il existe ! 🫣
    file_path = "dist/agent"
    if not os.path.exists(file_path):
        with open("fallback.exe", "w") as f:
            f.write("Erreur de compilation")
        file_path = "fallback.exe"
        
    return FileResponse(file_path, media_type="application/x-msdownload", filename="AnkyloAgent.exe")