import os
from fastapi import APIRouter, HTTPException, Depends
from app.scanner.main import run_scan
from app.secu.main import verify_admin # Import de ta nouvelle fonction 🛡️

router = APIRouter(prefix="/scan")

@router.post("/quick")
async def scan_quick(admin=Depends(verify_admin)):
    """Lance un scan rapide si l'utilisateur est admin 🦖"""
    success = run_scan(1)
    if success:
        return {"message": "Scan rapide lancé ! ✨", "admin": admin.get("name")}
    raise HTTPException(status_code=500, detail="Erreur lors du scan rapide 😱")

@router.post("/security")
async def scan_security(admin=Depends(verify_admin)):
    """Lance un scan de sécurité si l'utilisateur est admin 🛡️"""
    success = run_scan(2)
    if success:
        return {"message": "Scan sécurité lancé ! ✨"}
    raise HTTPException(status_code=500, detail="Erreur lors du scan sécurité 😱")

@router.post("/full")
async def scan_full(admin=Depends(verify_admin)):
    """Lance un scan complet si l'utilisateur est admin 🥵"""
    success = run_scan(3)
    if success:
        return {"message": "Scan complet lancé ! ✨"}
    raise HTTPException(status_code=500, detail="Erreur lors du scan complet 😱")