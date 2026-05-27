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

        # Initialiser les 7 derniers jours à 0
        data_map = {}
        today = datetime.now()
        for i in range(7):
            day_str = (today - timedelta(days=(6 - i))).strftime('%Y-%m-%d')
            data_map[day_str] = {"vulns": 0, "logs": 0}

        # -------------------------------------------------------
        # FIX 1 : Compter TOUTES les vulnérabilités de TOUS les
        # scans du jour (pas juste le dernier scan via MAX(id_scan))
        # et sommer correctement les CVEs dans chaque port de chaque hôte
        # -------------------------------------------------------
        vuln_query = """
            SELECT DATE_FORMAT(s.Time, '%Y-%m-%d') AS log_date, v.text
            FROM Vuln v
            JOIN Scan s ON v.id_scan = s.id_scan
            WHERE s.Time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            AND s.status = 1
        """
        cursor.execute(vuln_query)
        for row in cursor.fetchall():
            date = row['log_date']
            if date not in data_map or not row['text']:
                continue
            try:
                # text = JSON list of {port, vulns:[...]}
                # On compte le nombre de ports qui ont au moins 1 vuln
                ports = json.loads(row['text'])
                count = sum(
                    1
                    for port in ports
                    if isinstance(port, dict) and len(port.get('vulns', [])) > 0
                )
                data_map[date]["vulns"] += count
            except Exception as e:
                pass

        # -------------------------------------------------------
        # FIX 2 : Élargir la fenêtre logs à 8 jours pour absorber
        # le décalage UTC/heure locale (UTC+2 en France)
        # -------------------------------------------------------
        log_query = """
            SELECT DATE(CONVERT_TZ(timestamp, '+00:00', '+02:00')) AS log_date,
                   COUNT(*) AS log_count
            FROM SystemLogs
            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 8 DAY)
            GROUP BY DATE(CONVERT_TZ(timestamp, '+00:00', '+02:00'))
        """
        cursor.execute(log_query)
        rows = cursor.fetchall()

        for row in rows:
            date_str = str(row['log_date'])
            if date_str in data_map:
                data_map[date_str]["logs"] = row['log_count']

        result = [{"date": date, "vulns": val["vulns"], "logs": val["logs"]} for date, val in data_map.items()]
        return result

    except mysql.connector.Error as e:
        print(f"Graph Error: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
