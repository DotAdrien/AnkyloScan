import os
import threading
from fastapi import APIRouter, Depends  # Ajout de Depends 🛡️
from pydantic import BaseModel
from app.secu.main import verify_admin  # Import de la sécurité centralisée 🦖

router = APIRouter(prefix="/plan", tags=["Planificateur ⏰"])
PLAN_FILE = "/app/outputs/schedule.txt"

class PlanConfig(BaseModel):
    frequency: int
    scan_type: int

def background_scheduler(freq_hours, scan_type):
    import time
    from app.api.scan import create_pending_scan, background_scan_task
    while True:
        print(f"Tigrounet lance le scan automatique type {scan_type}...")
        scan_id = create_pending_scan(scan_type)
        background_scan_task(scan_type, scan_id)
        time.sleep(freq_hours * 3600)

@router.post("/save")
async def save_plan(config: PlanConfig, admin=Depends(verify_admin)):
    """
    Seul un admin avec un token valide peut modifier la planification 🔐
    L'objet 'admin' contient les infos du token si besoin.
    """
    os.makedirs(os.path.dirname(PLAN_FILE), exist_ok=True)
    with open(PLAN_FILE, "w") as f:
        f.write(f"{config.frequency}\n{config.scan_type}")

    thread = threading.Thread(target=background_scheduler, args=(config.frequency, config.scan_type))
    thread.daemon = True
    thread.start()

    return {
        "status": "success", 
        "message": f"Planification activée par {admin.get('name')} ! 🦖✨"
    }