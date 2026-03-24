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
            data_map[day_str] = 0

        query = """
            SELECT DATE_FORMAT(Scan.Time, '%Y-%m-%d') as log_date, Vuln.text
            FROM Vuln
            JOIN Scan ON Vuln.id_scan = Scan.id_scan
            WHERE Scan.Time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """
        cursor.execute(query)
        results = cursor.fetchall()

        for row in results:
            if row['log_date'] in data_map and row['text']:
                try:
                    vulns = json.loads(row['text'])
                    data_map[row['log_date']] += len(vulns)
                except Exception:
                    pass

        return [{"date": date, "count": count} for date, count in data_map.items()]

    except mysql.connector.Error as e:
        print(f"Graph Error: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()