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

        # Compte le nombre total de scans
        cursor.execute("SELECT COUNT(*) FROM Scan")
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
    """Récupère les données pour le graphique (Scans par jour sur les 7 derniers jours)."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # On groupe les scans par date (Format YYYY-MM-DD)
        query = """
            SELECT DATE_FORMAT(Time, '%Y-%m-%d') as date, COUNT(*) as count 
            FROM Scan 
            GROUP BY DATE_FORMAT(Time, '%Y-%m-%d') 
            ORDER BY date DESC 
            LIMIT 7
        """
        cursor.execute(query)
        data = cursor.fetchall()
        
        # On remet dans l'ordre chronologique pour le graphique
        data.reverse()
        
        return data

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur DB: {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
