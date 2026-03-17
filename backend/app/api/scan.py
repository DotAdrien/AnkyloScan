import os
import json
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.scanner.main import run_scan
from app.secu.main import verify_admin # Import de ta nouvelle fonction 🛡️
from app.db import get_db_connection
from app.api.database import parse_scan_expert

router = APIRouter(prefix="/scan")

def create_pending_scan(scan_type: int) -> int:
    """Crée une entrée 'En cours' dans la DB et retourne son ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Scan (Type, file_path, status) VALUES (%s, 'pending', 0)", (str(scan_type),))
    pending_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return pending_id

def process_scan_bg(scan_type: int, pending_id: int):
    """Tâche de fond globale qui lance le scan et met à jour la base 🌍"""
    # 1. Lancement du scan (Processus long bloquant)
    success = run_scan(scan_type)
    
    # 2. Une fois terminé, archivage et nettoyage des statuts
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if success and scan_type == 3:
            # --- AUTOMATISATION : Remplissage de la table Vuln ---
            cursor.execute("SELECT id_scan, file_path FROM Scan WHERE Type='3' AND status=1 ORDER BY id_scan DESC LIMIT 1")
            last_scan = cursor.fetchone()

            if last_scan:
                scan_id = last_scan['id_scan']
                file_path = last_scan['file_path']

                base_dir = os.path.abspath("/app/outputs") if os.name != 'nt' else os.path.abspath("outputs")
                filename = os.path.basename(file_path)
                safe_path = os.path.join(base_dir, filename)

                if os.path.exists(safe_path):
                    with open(safe_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    vuln_results = parse_scan_expert(content)

                    for host in vuln_results:
                        ip = host['ip']
                        vulns_json = json.dumps(host['vulns'], ensure_ascii=False)
                        
                        cursor.execute(
                            "INSERT INTO Vuln (id_scan, hosts, text) VALUES (%s, %s, %s)",
                            (scan_id, ip, vulns_json)
                        )
                    conn.commit()

                    # --- NETTOYAGE : Un seul scan complet par jour ---
                    cursor.execute("""
                        DELETE FROM Scan 
                        WHERE DATE(Time) = CURDATE() AND Type = '3' AND status = 1 AND id_scan != %s
                    """, (scan_id,))
                    conn.commit()
                    print(f"✅ Vulnérabilités archivées pour le scan #{scan_id}")

        # 3. Suppression du marqueur 'En cours' (le vrai log a été créé par run_scan avec status=1)
        cursor.execute("DELETE FROM Scan WHERE id_scan = %s", (pending_id,))
        conn.commit()

    except Exception as e:
        print(f"⚠️ Erreur Background Task : {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.post("/quick")
async def scan_quick(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    pending_id = create_pending_scan(1)
    background_tasks.add_task(process_scan_bg, 1, pending_id)
    return {"message": "Scan rapide lancé en arrière-plan ! ✨", "admin": admin.get("name")}

@router.post("/security")
async def scan_security(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    pending_id = create_pending_scan(2)
    background_tasks.add_task(process_scan_bg, 2, pending_id)
    return {"message": "Scan sécurité lancé en arrière-plan ! ✨"}

@router.post("/full")
async def scan_full(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    pending_id = create_pending_scan(3)
    background_tasks.add_task(process_scan_bg, 3, pending_id)
    return {"message": "Scan complet lancé en arrière-plan ! ✨"}