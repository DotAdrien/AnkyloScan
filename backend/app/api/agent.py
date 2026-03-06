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
    host = request.base_url.hostname
    
    # Enregistrement du token 💾
    conn = mysql.connector.connect(host="db", user="root", password=DB_PASSWORD, database="ankyloscan")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Agents (token) VALUES (%s)", (token,))
    conn.commit()
    cursor.close()
    conn.close()
    
    # Lecture du template externe 📂
    template_path = os.path.join(os.path.dirname(__file__), "agent", "ad.py")
    with open(template_path, "r") as f:
        script_content = f.read().replace("{SERVER_IP}", host).replace("{TOKEN}", token)
        
    return Response(
        content=script_content, 
        media_type="text/x-python", 
        headers={"Content-Disposition": "attachment; filename=ad.py"}
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