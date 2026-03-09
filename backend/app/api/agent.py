import os
import subprocess
import secrets
import mysql.connector # type: ignore
from fastapi import APIRouter, Request, Response, Depends, HTTPException
from fastapi.responses import FileResponse
from app.secu.main import verify_admin 

router = APIRouter(prefix="/agent", tags=["Agent 🤖"])
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

@router.get("/download")
async def get_script(request: Request):
    # 1. Génère le fichier temporaire (ton code actuel)
    token = secrets.token_hex(16)
    script_path = "/tmp/ad.py"
    with open(script_path, "w") as f:
        f.write(...) # Ton code template ici

    # 2. Compile en .exe via Docker
    exe_path = "/tmp/ad.exe"
    subprocess.run([
        "docker", "run", "--rm",
        "-v", f"{script_path}:/app/ad.py",
        "-v", "/tmp:/dist", # Partage le dossier
        "agent-builder", "pyinstaller", "--onefile", "--distpath", "/dist", "ad.py"
    ], check=True)

    # 3. Retourne le fichier .exe
    return FileResponse(exe_path, filename="AnkyloAgent.exe")



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