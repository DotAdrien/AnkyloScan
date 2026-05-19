from datetime import datetime, timedelta
import json
import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Depends
from app.secu.main import verify_admin
from app.secu.db import get_db_connection

router = APIRouter(prefix="/dashboard", tags=["Dashboard 📊"])

@router.get("/stats")
def get_stats(admin=Depends(verify_admin)):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Scan WHERE Time >= NOW() - INTERVAL 24 HOUR")
        scan_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Agents")
        agent_count = cursor.fetchone()[0]

        return {
            "scans": scan_count,
            "agents": agent_count
        }

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.get("/graph")
def get_graph_data(admin=Depends(verify_admin)):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        data_map = {}
        today = datetime.now()
        for i in range(7):
            day_str = (today - timedelta(days=(6 - i))).strftime('%Y-%m-%d')
            data_map[day_str] = {"vulns": 0, "logs": 0}

        # 1. Récupérer les vulnérabilités du scan LE PLUS RÉCENT par jour
        vuln_query = """
            SELECT DATE_FORMAT(Scan.Time, '%Y-%m-%d') as log_date, Vuln.text
            FROM Vuln
            JOIN Scan ON Vuln.id_scan = Scan.id_scan
            WHERE Scan.id_scan IN (
                SELECT MAX(id_scan)
                FROM Scan
                WHERE Time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(Time)
            )
        """
        cursor.execute(vuln_query)
        vuln_results = cursor.fetchall()

        for row in vuln_results:
            if row['log_date'] in data_map and row['text']:
                try:
                    vulns = json.loads(row['text'])
                    # On remplace par le nombre du dernier scan
                    data_map[row['log_date']]["vulns"] = len(vulns)
                except Exception:
                    pass

        # 2. Récupérer le nombre de logs des agents par jour
        log_query = """
            SELECT DATE_FORMAT(Time, '%Y-%m-%d') as log_date, COUNT(*) as log_count
            FROM Logs
            WHERE Time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(Time)
        """
        try:
            cursor.execute(log_query)
            log_results = cursor.fetchall()
            for row in log_results:
                if row['log_date'] in data_map:
                    data_map[row['log_date']]["logs"] = row['log_count']
        except mysql.connector.Error:
            # Si la table Logs n'existe pas encore ou erreur, on laisse à 0
            pass

        return [{"date": date, "vulns": val["vulns"], "logs": val["logs"]} for date, val in data_map.items()]

    except mysql.connector.Error as e:
        print(f"Graph Error: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()