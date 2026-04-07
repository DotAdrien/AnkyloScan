from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import mysql.connector # type: ignore
import os
from app.secu.main import verify_admin
from app.api.email_sender import send_agent_log_alert
from app.secu.db import get_db_connection

router = APIRouter(prefix="/logs", tags=["Logs 🛡️"])
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

class LogEntry(BaseModel):
    token: str
    event_id: int
    source: str
    message: str

@router.post("/ingest")
def ingest_logs(log: LogEntry):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM Agents WHERE token = %s", (log.token,))
    agent = cursor.fetchone()
    if not agent:
        print(f"⚠️ LOG REJECTED: Invalid or unknown token received -> {log.token}")
        cursor.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Unauthorized Agent 🚫")

    cursor.execute("SELECT id_log FROM SystemLogs WHERE event_id = %s AND source = %s AND message = %s AND timestamp > NOW() - INTERVAL 1 MINUTE", (log.event_id, log.source, log.message))
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute("INSERT INTO SystemLogs (event_id, source, message) VALUES (%s, %s, %s)", (log.event_id, log.source, log.message))
        conn.commit()

        send_agent_log_alert(log.source, log.event_id, log.message)

    cursor.close()
    conn.close()
    return {"status": "Log received! ✨"}

@router.get("/")
def get_logs(admin=Depends(verify_admin)):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM SystemLogs ORDER BY timestamp DESC LIMIT 50")
        logs = cursor.fetchall()
        for log in logs:
            if log["timestamp"]:
                log["timestamp"] = log["timestamp"].strftime("%m/%d/%Y - %H:%M")
        return logs
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail="Database error 😱")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()