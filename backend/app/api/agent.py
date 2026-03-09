import os
import subprocess
import secrets
import mysql.connector # type: ignore
from fastapi import APIRouter, Request, Response, Depends, HTTPException
from fastapi.responses import FileResponse
from app.secu.main import verify_admin 

router = APIRouter(prefix="/agent", tags=["Agent 🤖"])
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

import requests
from fastapi.responses import Response

@router.get("/download")
async def get_script(request: Request):
    token = secrets.token_hex(16)
    
    # On demande au conteneur "compiler" de faire le travail 🥵
    rep = requests.post("http://compiler:8002/build", json={"token": token, "ip": SERVER_IP})
    
    # On renvoie le fichier .exe généré directement à l'utilisateur ✨
    return Response(content=rep.content, media_type="application/x-msdownload", headers={"Content-Disposition": "attachment; filename=AnkyloAgent.exe"})



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