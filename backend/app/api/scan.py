from fastapi import APIRouter, Depends, BackgroundTasks
from app.secu.main import verify_admin # Import de ta nouvelle fonction 🛡️
from app.scanner.tasks import create_pending_scan, background_scan_task

router = APIRouter(prefix="/scan")

@router.post("/quick")
async def scan_quick(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    """Lance un scan rapide en arrière-plan si l'utilisateur est admin 🦖"""
    scan_id = create_pending_scan(1)
    background_tasks.add_task(background_scan_task, 1, scan_id)
    return {"message": "Scan rapide lancé en arrière-plan ! ✨ Tu peux suivre l'avancée dans l'historique.", "admin": admin.get("name")}

@router.post("/security")
async def scan_security(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    """Lance un scan de sécurité en arrière-plan si l'utilisateur est admin 🛡️"""
    scan_id = create_pending_scan(2)
    background_tasks.add_task(background_scan_task, 2, scan_id)
    return {"message": "Scan sécurité lancé en arrière-plan ! ✨ Tu peux suivre l'avancée dans l'historique."}

@router.post("/full")
async def scan_full(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    """Lance un scan complet en arrière-plan si l'utilisateur est admin 🥵"""
    scan_id = create_pending_scan(3)
    background_tasks.add_task(background_scan_task, 3, scan_id)
    return {"message": "Scan complet lancé en arrière-plan ! ✨ Tu peux suivre l'avancée dans l'historique."}