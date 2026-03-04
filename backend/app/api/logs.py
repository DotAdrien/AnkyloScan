from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import mysql.connector # type: ignore
import os
from app.secu.main import verify_admin # Sécurité 🛡️

router = APIRouter(prefix="/logs", tags=["Logs 🛡️"])
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

class LogEntry(BaseModel):
    event_id: int
    source: str
    message: str

@router.post("/ingest")
def ingest_logs(log: LogEntry):
    conn = mysql.connector.connect(host="db", user="root", password=DB_PASSWORD, database="ankyloscan")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SystemLogs (event_id, source, message) VALUES (%s, %s, %s)", 
                   (log.event_id, log.source, log.message))
    conn.commit()
    conn.close()
    return {"status": "Log reçu ! ✨"}

@router.get("/")
def get_logs(admin=Depends(verify_admin)):
    conn = None
    try:
        conn = mysql.connector.connect(host="db", user="root", password=DB_PASSWORD, database="ankyloscan")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM SystemLogs ORDER BY timestamp DESC LIMIT 50")
        logs = cursor.fetchall()
        for log in logs:
            if log["timestamp"]:
                log["timestamp"] = log["timestamp"].strftime("%d/%m/%Y - %H:%M")
        return logs
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail="Erreur base de données 😱")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()