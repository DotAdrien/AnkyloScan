import os
import threading
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.secu.main import verify_admin

router = APIRouter(prefix="/plan", tags=["Scheduler ⏰"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN_FILE = os.path.join(BASE_DIR, "outputs", "schedule.txt")

scheduler_thread = None
stop_event = threading.Event()

class PlanConfig(BaseModel):
    frequency: int
    scan_type: int

def background_scheduler(freq_hours, scan_type, stop_event_ref):
    from app.scanner.tasks import create_pending_scan, background_scan_task
    while not stop_event_ref.is_set():
        print(f"System launching automatic scan type {scan_type}...")
        scan_id = create_pending_scan(scan_type)
        background_scan_task(scan_type, scan_id)
        stop_event_ref.wait(freq_hours * 3600)

@router.post("/save")
async def save_plan(config: PlanConfig, admin=Depends(verify_admin)):
    global scheduler_thread, stop_event

    os.makedirs(os.path.dirname(PLAN_FILE), exist_ok=True)
    with open(PLAN_FILE, "w") as f:
        f.write(f"{config.frequency}\n{config.scan_type}")

    if scheduler_thread is not None and scheduler_thread.is_alive():
        stop_event.set()
        scheduler_thread.join(timeout=2.0)
        stop_event.clear()

    scheduler_thread = threading.Thread(
        target=background_scheduler, 
        args=(config.frequency, config.scan_type, stop_event)
    )
    scheduler_thread.daemon = True
    scheduler_thread.start()

    return {
        "status": "success", 
        "message": f"Scheduling activated by {admin.get('name')}! 🦖✨"
    }