import os
import re
import json
import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from app.secu.main import verify_admin
from app.secu.db import get_db_connection

router = APIRouter(prefix="/db", tags=["Database 🐬"])

@router.get("/history")
def get_scan_history(admin=Depends(verify_admin)):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT id_scan as id, type, Time as time, file_path, status 
            FROM Scan 
            ORDER BY Time DESC 
            LIMIT 5
        """
        cursor.execute(query)
        scans = cursor.fetchall()
        
        descriptions = {
            1: "Quick scan completed. ✨",
            2: "Port and MAC address detection completed. 👍",
            3: "Full vulnerability analysis completed. 🦖"
        }

        descriptions_pending = {
            1: "Quick scan in progress... ⏳",
            2: "Port and MAC address detection in progress... ⏳",
            3: "Full vulnerability analysis in progress... 🧠⏳"
        }

        for scan in scans:
            scan_type = int(scan["type"]) if scan["type"] else 1
            if scan["status"] == 0:
                scan["description"] = descriptions_pending.get(scan_type, "Scan in progress... ⏳")
            else:
                scan["description"] = descriptions.get(scan_type, "Scan performed. 🛡️")

            if scan["time"]:
                scan["time"] = scan["time"].strftime("%m/%d/%Y - %H:%M")

        return scans

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)} 😱")
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.get("/report")
def get_report_file(path: str, admin=Depends(verify_admin)):
    base_dir = os.path.abspath("/app/outputs") if os.name != 'nt' else os.path.abspath("outputs")
    filename = os.path.basename(path)
    safe_path = os.path.join(base_dir, filename)

    if not filename.startswith("scan_") or filename in ["email.txt", "schedule.txt"]:
        raise HTTPException(status_code=403, detail="Access denied to this file 🚫")

    if os.path.exists(safe_path) and os.path.isfile(safe_path):
        return FileResponse(safe_path)
    raise HTTPException(status_code=404, detail="Report not found 😱")

@router.get("/vulns")
def get_vulns_analysis(path: str, admin=Depends(verify_admin)):
    base_dir = os.path.abspath("/app/outputs") if os.name != 'nt' else os.path.abspath("outputs")
    filename = os.path.basename(path)
    safe_path = os.path.join(base_dir, filename)

    if not filename.startswith("scan_") or filename in ["email.txt", "schedule.txt"]:
        raise HTTPException(status_code=403, detail="Access denied 🚫")

    if not filename.startswith("scan_3_"):
        raise HTTPException(status_code=400, detail="This analysis is restricted to full scans (Level 3).")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id_scan FROM Scan WHERE file_path = %s", (safe_path,))
        scan_entry = cursor.fetchone()
        
        if not scan_entry:
            raise HTTPException(status_code=404, detail="Scan entry not found in database for this report.")
        
        scan_id = scan_entry['id_scan']
        
        cursor.execute("SELECT hosts, text FROM Vuln WHERE id_scan = %s", (scan_id,))
        vuln_records = cursor.fetchall()
        
        results = []
        for record in vuln_records:
            results.append({
                "ip": record['hosts'],
                "ports": json.loads(record['text'])
            })
        
        return results

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()