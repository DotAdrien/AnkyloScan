from fastapi import APIRouter, Depends, BackgroundTasks
from app.secu.main import verify_admin
from app.scanner.tasks import create_pending_scan, background_scan_task

router = APIRouter(prefix="/scan")

@router.post("/quick")
async def scan_quick(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    scan_id = create_pending_scan(1)
    background_tasks.add_task(background_scan_task, 1, scan_id)
    return {"message": "Quick scan launched in the background! ✨ You can follow the progress in the history.", "admin": admin.get("name")}

@router.post("/security")
async def scan_security(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    scan_id = create_pending_scan(2)
    background_tasks.add_task(background_scan_task, 2, scan_id)
    return {"message": "Security scan launched in the background! ✨ You can follow the progress in the history."}

@router.post("/full")
async def scan_full(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    scan_id = create_pending_scan(3)
    background_tasks.add_task(background_scan_task, 3, scan_id)
    return {"message": "Full scan launched in the background! ✨ You can follow the progress in the history."}
