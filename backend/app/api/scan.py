import os
import jwt
from fastapi import APIRouter, HTTPException, Depends, Cookie
from app.scanner.main import run_scan

router = APIRouter(prefix="/scan")

DB_PASSWORD = os.getenv("ADMIN_PASSWORD")
ALGORITHM = "HS256"


# a inclure partout
def get_admin_user(session_token: str = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Non connecté 😶")
    try:
        payload = jwt.decode(session_token, DB_PASSWORD, algorithms=[ALGORITHM])
        if payload.get("rank") != "admin":
            raise HTTPException(status_code=403, detail="Accès réservé aux admins ! 🚫")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Session invalide 😱")
# jusqu'a la

@router.post("/quick")
async def scan_quick(admin=Depends(get_admin_user)):
    success = run_scan(1)
    if success:
        return {"message": "Scan rapide lancé ! ✨"}
    raise HTTPException(status_code=500, detail="Erreur lors du scan rapide 😱")

@router.post("/security")
async def scan_security(admin=Depends(get_admin_user)):
    success = run_scan(2)
    if success:
        return {"message": "Scan sécurité lancé ! ✨"}
    raise HTTPException(status_code=500, detail="Erreur lors du scan sécurité 😱")

@router.post("/full")
async def scan_full(admin=Depends(get_admin_user)):
    success = run_scan(3)
    if success:
        return {"message": "Scan complet lancé ! ✨"}
    raise HTTPException(status_code=500, detail="Erreur lors du scan complet 😱")