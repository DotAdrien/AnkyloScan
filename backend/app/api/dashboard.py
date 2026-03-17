from datetime import datetime, timedelta
import json
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
    """Récupère les logs réels des agents sur les 7 derniers jours."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. On initialise les 7 derniers jours à 0 pour avoir un axe X continu
        data_map = {}
        today = datetime.now()
        for i in range(7):
            day_str = (today - timedelta(days=(6 - i))).strftime('%Y-%m-%d')
            data_map[day_str] = 0

        # 2. Requête SQL : Compte les logs groupés par jour
        query = """
            SELECT DATE_FORMAT(Scan.Time, '%Y-%m-%d') as log_date, Vuln.text
            FROM Vuln
            JOIN Scan ON Vuln.id_scan = Scan.id_scan
            WHERE Scan.Time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # 3. Remplissage avec les vraies données
        for row in results:
            if row['log_date'] in data_map and row['text']:
                try:
                    vulns = json.loads(row['text'])
                    data_map[row['log_date']] += len(vulns)
                except Exception:
                    pass

        # 4. Formatage pour le frontend
        return [{"date": date, "count": count} for date, count in data_map.items()]

    except mysql.connector.Error as e:
        print(f"Erreur Graphique: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
