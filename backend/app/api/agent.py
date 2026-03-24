import os
import secrets
import socket
import mysql.connector # type: ignore
from fastapi import APIRouter, Request, Response, Depends, HTTPException
from app.secu.main import verify_admin 
from app.secu.db import get_db_connection

router = APIRouter(prefix="/agent", tags=["Agent 🤖"])

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

async def generate_agent_download(filename_on_disk: str, filename_download: str):
    token = secrets.token_hex(16)
    server_ip = get_host_ip()
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Agents (token) VALUES (%s)", (token,))
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database connection error... 😱")
    finally:
        if conn and conn.is_connected():
            conn.close()

    try:
        with open(f"app/api/agent/{filename_on_disk}", "r") as f:
            ps1_content = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"File {filename_on_disk} not found 😱")
    
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
    return await generate_agent_download("agent3.sh", "InstallAnkyloAgent3.sh")

@router.delete("/clear")
async def clear_agents(admin=Depends(verify_admin)):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE Agents")
        conn.commit()
        cursor.close()
        return {"status": "success", "message": "Agent table cleared! 😌"}
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Error during cleanup 😱")
    finally:
        if conn and conn.is_connected():
            conn.close()