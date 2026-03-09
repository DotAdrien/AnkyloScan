import os
import requests
import secrets
import mysql.connector # type: ignore
from fastapi import APIRouter, Request, Response, Depends, HTTPException
from app.secu.main import verify_admin 

router = APIRouter(prefix="/agent", tags=["Agent 🤖"])
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

@router.get("/download")
async def get_script(request: Request):
    token = secrets.token_hex(16)
    
    # 1. On récupère dynamiquement l'IP du serveur 🌐
    server_ip = "192.168.2.103"
    
    # 2. On sauvegarde le token en base pour autoriser l'agent 💾
    conn = None
    try:
        conn = mysql.connector.connect(host="db", user="root", password=DB_PASSWORD, database="ankyloscan")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Agents (token) VALUES (%s)", (token,))
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="La base de données boude... 😱")
    finally:
        if conn and conn.is_connected():
            conn.close()

    # On demande au conteneur "compiler" de faire le travail 🥵
    try:
        rep = requests.post("http://compiler:8002/build", json={"token": token, "ip": server_ip})
        rep.raise_for_status()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Échec de la compilation de l'agent 😩")
    
    # On renvoie le fichier .exe généré directement à l'utilisateur ✨
    return Response(
        content=rep.content, 
        media_type="application/x-msdownload", 
        headers={"Content-Disposition": "attachment; filename=AnkyloAgent.exe"}
    )

@router.delete("/clear")
async def clear_agents(admin=Depends(verify_admin)):
    """Supprime tous les agents enregistrés 🧹"""
    conn = None
    try:
        conn = mysql.connector.connect(host="db", user="root", password=DB_PASSWORD, database="ankyloscan")
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