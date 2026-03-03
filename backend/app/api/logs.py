from fastapi import APIRouter
from pydantic import BaseModel
import mysql.connector # type: ignore
import os

router = APIRouter(prefix="/logs", tags=["Logs 🛡️"])
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

class LogEntry(BaseModel):
    event_id: int
    source: str
    message: str

@router.post("/ingest")
def ingest_logs(log: LogEntry):
    # Insère les logs en base (pense à créer la table SystemLogs en SQL)
    conn = mysql.connector.connect(host="db", user="root", password=DB_PASSWORD, database="ankyloscan")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SystemLogs (event_id, source, message) VALUES (%s, %s, %s)", 
                   (log.event_id, log.source, log.message))
    conn.commit()
    conn.close()
    return {"status": "Log reçu ! ✨"}