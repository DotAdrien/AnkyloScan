import os
import secrets
import mysql.connector
from fastapi import APIRouter, Request, Response, Depends
from app.secu.main import verify_admin

router = APIRouter(prefix="/agent", tags=["Agent 🤖"])
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

@router.get("/download")
async def get_script(request: Request):
    # Récupère l'IP du serveur pour le script
    host = request.base_url.hostname
    token = secrets.token_hex(16)
    
    script_content = f"""
import requests
SERVER_IP = "{host}"
TOKEN = "{token}"
print(f"Agent configuré pour {{SERVER_IP}}")
# Logique de ton agent ici...
"""
    return Response(content=script_content, media_type="text/x-python", headers={"Content-Disposition": "attachment; filename=agent.py"})

@router.post("/register")
async def register_agent(token: str, ip: str):
    conn = mysql.connector.connect(host="db", user="root", password=DB_PASSWORD, database="ankyloscan")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Agents (token, ip) VALUES (%s, %s)", (token, ip))
    conn.commit()
    conn.close()
    return {"status": "success"}