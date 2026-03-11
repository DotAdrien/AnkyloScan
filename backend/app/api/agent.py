import os
import secrets
import mysql.connector # type: ignore
from fastapi import APIRouter, Request, Response, Depends, HTTPException
from app.secu.main import verify_admin 
from app.db import get_db_connection

router = APIRouter(prefix="/agent", tags=["Agent 🤖"])

async def generate_agent_download(filename_on_disk: str, filename_download: str):
    """Génère le script d'agent avec token unique et l'envoie"""
    token = secrets.token_hex(16)
    server_ip = "192.168.2.103"
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Agents (token) VALUES (%s)", (token,))
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="La base de données boude... 😱")
    finally:
        if conn and conn.is_connected():
            conn.close()

    # Lecture du fichier PowerShell 📄
    try:
        with open(f"app/api/agent/{filename_on_disk}", "r") as f:
            ps1_content = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Fichier {filename_on_disk} introuvable 😱")
    
    # On remplace les variables ✨
    ps1_content = ps1_content.replace("SERVER_IP_PLACEHOLDER", server_ip)
    ps1_content = ps1_content.replace("TOKEN_PLACEHOLDER", token)

    return Response(
        content=ps1_content, 
        media_type="text/plain", 
        headers={"Content-Disposition": f"attachment; filename={filename_download}"}
    )

@router.get("/download")
async def get_script(request: Request):
    return await generate_agent_download("ad.ps1", "InstallAnkyloAgent.ps1")

@router.get("/download2")
async def get_script_2(request: Request):
    return await generate_agent_download("agent2.ps1", "InstallAnkyloAgent2.ps1")

@router.get("/download3")
async def get_script_3(request: Request):
    return await generate_agent_download("agent3.ps1", "InstallAnkyloAgent3.ps1")

@router.delete("/clear")
async def clear_agents(admin=Depends(verify_admin)):
    """Supprime tous les agents enregistrés 🧹"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE Agents") # Vide la table 🚫
        conn.commit()
        cursor.close()
        return {"status": "success", "message": "Table des agents vidée ! 😌"}
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Erreur lors du nettoyage 😱")
    finally:
        if conn and conn.is_connected():
            conn.close()