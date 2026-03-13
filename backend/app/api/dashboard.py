from datetime import datetime, timedelta
import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Depends
from app.secu.main import verify_admin
from app.db import get_db_connection

router = APIRouter(prefix="/dashboard", tags=["Dashboard 📊"])

@router.get("/stats")
def get_stats(admin=Depends(verify_admin)):
    """Récupère les statistiques globales pour les cartes du dashboard."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Compte le nombre de scans des dernières 24h
        cursor.execute("SELECT COUNT(*) FROM Scan WHERE Time >= NOW() - INTERVAL 24 HOUR")
        scan_count = cursor.fetchone()[0]

        # Compte le nombre d'agents enregistrés
        cursor.execute("SELECT COUNT(*) FROM Agents")
        agent_count = cursor.fetchone()[0]

        return {
            "scans": scan_count,
            "agents": agent_count
        }

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur DB: {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.get("/graph")
def get_graph_data(admin=Depends(verify_admin)):
    """Récupère des fausses données pour le graphique (Mode Démo/Dev)."""
    data = []
    today = datetime.now()
    
    # Valeurs arbitraires pour simuler une activité sur 7 jours
    fake_counts = [2, 8, 15, 5, 12, 4, 9]
    
    for i in range(7):
        # On calcule la date pour chaque jour (J-6 à J-0)
        date = today - timedelta(days=(6 - i))
        data.append({
            "date": date.strftime('%Y-%m-%d'),
            "count": fake_counts[i]
        })
    
    return data
