import os
import secrets
import mysql.connector # type: ignore
from fastapi import APIRouter, Request, Response, Depends, HTTPException
from app.secu.main import verify_admin 

router = APIRouter(prefix="/agent", tags=["Agent 🤖"])
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

@router.get("/download")
async def get_script(request: Request):
    token = secrets.token_hex(16)
    server_ip = "192.168.2.103"
    
    conn = None
    try:
        conn = mysql.connector.connect(host="127.0.0.1", user="root", password=DB_PASSWORD, database="ankyloscan")
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
        with open("app/api/agent/ad.ps1", "r") as f:
            ps1_content = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Fichier ad.ps1 introuvable 😱")
    
    # On remplace les variables ✨
    ps1_content = ps1_content.replace("SERVER_IP_PLACEHOLDER", server_ip)
    ps1_content = ps1_content.replace("TOKEN_PLACEHOLDER", token)

    return Response(
        content=ps1_content, 
        media_type="text/plain", 
        headers={"Content-Disposition": "attachment; filename=InstallAnkyloAgent.ps1"}
    )

@router.delete("/clear")
async def clear_agents(admin=Depends(verify_admin)):
    """Supprime tous les agents enregistrés 🧹"""
    conn = None
    try:
        conn = mysql.connector.connect(host="127.0.0.1", user="root", password=DB_PASSWORD, database="ankyloscan")
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