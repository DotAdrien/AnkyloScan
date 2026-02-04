import os
import jwt
from fastapi import APIRouter, HTTPException, Depends, Cookie
from pydantic import BaseModel
import subprocess

router = APIRouter(prefix="/scan")

DB_PASSWORD = os.getenv("ADMIN_PASSWORD")
ALGORITHM = "HS256"

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

async def run_nmap(args: list):
    """Exécute nmap avec les arguments fournis 🚀"""
    try:
        result = subprocess.run(["nmap"] + args, capture_output=True, text=True, check=True)
        return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Erreur nmap : {e.stderr}")

@router.post("/quick")
async def scan_quick(admin=Depends(get_admin_user)):
    # Scan rapide : Détection d'OS (-O) sur le réseau local
    return await run_nmap(["-F", "-O", "192.168.1.0/24"])

@router.post("/security")
async def scan_security(admin=Depends(get_admin_user)):
    # Scan sécurité : Ports et adresses MAC
    return await run_nmap(["-sP", "192.168.1.0/24"])

@router.post("/full")
async def scan_full(admin=Depends(get_admin_user)):
    # Scan complet : Versions (-sV) et scripts de vulnérabilités (--script vuln)
    return await run_nmap(["-sV", "--script", "vuln", "192.168.1.0/24"])