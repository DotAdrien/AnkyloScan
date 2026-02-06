import os
import time
import threading
from fastapi import APIRouter
from pydantic import BaseModel
from app.scanner.main import run_scan # On importe la fonction de scan

router = APIRouter(prefix="/plan", tags=["Planificateur ⏰"])
PLAN_FILE = "/app/outputs/schedule.txt"

class PlanConfig(BaseModel):
    frequency: int
    scan_type: int

def background_scheduler(freq_hours, scan_type):
    """La boucle qui tourne sur le serveur 24h/24 🦖"""
    while True:
        print(f"Tigrounet lance le scan automatique type {scan_type}...")
        run_scan(scan_type) # Lance le vrai scan
        time.sleep(freq_hours * 3600) # Attend en secondes

@router.post("/save")
async def save_plan(config: PlanConfig):
    # 1. Sauvegarde pour la trace 📝
    os.makedirs(os.path.dirname(PLAN_FILE), exist_ok=True)
    with open(PLAN_FILE, "w") as f:
        f.write(f"{config.frequency}\n{config.scan_type}")

    # 2. On lance la boucle dans un thread séparé 🚀
    # Comme ça, le serveur continue de répondre pendant que Tigrounet compte les heures
    thread = threading.Thread(target=background_scheduler, args=(config.frequency, config.scan_type))
    thread.daemon = True # S'arrête si le serveur s'arrête
    thread.start()

    return {"status": "success", "message": "Planification activée sur le serveur ! 🦖✨"}