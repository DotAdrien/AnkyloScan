from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import mysql.connector # type: ignore
import os
from app.secu.main import verify_admin # Sécurité 🛡️
from app.api.email_sender import send_alert_email, get_current_email_config # type: ignore # Import pour l'envoi d'emails
from app.db import get_db_connection

router = APIRouter(prefix="/logs", tags=["Logs 🛡️"])
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

class LogEntry(BaseModel):
    token: str  # Ajout pour identifier l'agent 🤖
    event_id: int
    source: str
    message: str

@router.post("/ingest")
def ingest_logs(log: LogEntry):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Vérification du token 🔐
    cursor.execute("SELECT id FROM Agents WHERE token = %s", (log.token,))
    agent = cursor.fetchone()
    if not agent:
        print(f"⚠️ REJET LOG : Token invalide ou inconnu reçu -> {log.token}")
        cursor.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Agent non autorisé 🚫")

    # Vérification doublon (pour éviter spam)
    cursor.execute("SELECT id_log FROM SystemLogs WHERE event_id = %s AND source = %s AND message = %s AND timestamp > NOW() - INTERVAL 1 MINUTE", (log.event_id, log.source, log.message))
    exists = cursor.fetchone()
    
    if not exists:
        # INSERT manquant ! ✨
        cursor.execute("INSERT INTO SystemLogs (event_id, source, message) VALUES (%s, %s, %s)", (log.event_id, log.source, log.message))
        conn.commit()

        # --- ENVOI D'EMAIL POUR LES LOGS D'AGENT ---
        email_config = get_current_email_config()
        if email_config.agent_log_alerts:
            subject = f"🤖 Alerte AnkyloScan: Nouveau log d'agent ({log.source})"
            body = f"Un nouvel événement a été enregistré par un agent:\n\n"
            body += f"Source: {log.source}\nEvent ID: {log.event_id}\nMessage: {log.message}\n"
            body += "\nConnectez-vous à AnkyloScan pour consulter tous les logs."
            send_alert_email(subject, body)

    cursor.close()
    conn.close()
    return {"status": "Log reçu ! ✨"}

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
                log["timestamp"] = log["timestamp"].strftime("%d/%m/%Y - %H:%M")
        return logs
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail="Erreur base de données 😱")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()