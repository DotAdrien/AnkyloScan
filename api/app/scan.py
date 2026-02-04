import os
import jwt
from fastapi import APIRouter, HTTPException, Depends, Cookie
from pydantic import BaseModel
import subprocess

router = APIRouter(prefix="/scan")

# Configuration identique à account.py 🔑
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")
ALGORITHM = "HS256"

class ScanRequest(BaseModel):
    network: str  # Exemple: "192.168.1.0/24"

def get_admin_user(session_token: str = Cookie(None)):
    """Vérifie si l'utilisateur est connecté et admin 🛡️"""
    if not session_token:
        raise HTTPException(status_code=401, detail="Non connecté 😶")
    try:
        payload = jwt.decode(session_token, DB_PASSWORD, algorithms=[ALGORITHM])
        if payload.get("rank") != "admin":
            raise HTTPException(status_code=403, detail="Accès réservé aux admins ! 🚫")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Session invalide 😱")

@router.post("/start")
async def start_scan(request: ScanRequest, admin=Depends(get_admin_user)):
    network = request.network
    try:
        # Commande RustScan ultra-rapide 🚀
        # -a : adresse cible
        # -t 2000 : nombre de threads (ajustable selon ta puissance)
        # -b 1000 : batch size
        # -- -sV : passe l'argument -sV à nmap pour identifier les versions après le scan rapide
        command = ["rustscan", "-a", network, "-t", "2000", "-b", "1000", "--", "-sV"]
        
        process = subprocess.run(
            command, 
            capture_output=True, 
            text=True,
            check=True
        )
        
        return {
            "status": "success",
            "output": process.stdout,
            "message": "Scan RustScan terminé ! 🦖🔥"
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Erreur RustScan : {e.stderr}")