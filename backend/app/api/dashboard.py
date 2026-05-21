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

        print(f"[GRAPH] data_map keys: {list(data_map.keys())}")

        # 1. Vulnérabilités : dernier scan par jour
        vuln_query = """
            SELECT DATE_FORMAT(s.Time, '%Y-%m-%d') AS log_date, v.text
            FROM Vuln v
            JOIN Scan s ON v.id_scan = s.id_scan
            WHERE s.id_scan IN (
                SELECT MAX(id_scan)
                FROM Scan
                WHERE Time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(Time)
            )
        """
        cursor.execute(vuln_query)
        for row in cursor.fetchall():
            date = row['log_date']
            if date not in data_map or not row['text']:
                continue
            try:
                ports = json.loads(row['text'])
                count = sum(len(port.get('vulns', [])) for port in ports if isinstance(port, dict))
                data_map[date]["vulns"] += count
            except Exception:
                pass

        # 2. Logs agents par jour
        log_query = """
            SELECT DATE(timestamp) AS log_date, COUNT(*) AS log_count
            FROM SystemLogs
            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(timestamp)
        """
        cursor.execute(log_query)
        rows = cursor.fetchall()
        print(f"[GRAPH] log rows raw: {rows}")

        for row in rows:
            # DATE() retourne un objet datetime.date en Python, on le convertit en string
            date_str = str(row['log_date'])
            print(f"[GRAPH] log_date={date_str!r}, log_count={row['log_count']}, in data_map={date_str in data_map}")
            if date_str in data_map:
                data_map[date_str]["logs"] = row['log_count']

        result = [{"date": date, "vulns": val["vulns"], "logs": val["logs"]} for date, val in data_map.items()]
        print(f"[GRAPH] final result: {result}")
        return result

    except mysql.connector.Error as e:
        print(f"Graph Error: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
