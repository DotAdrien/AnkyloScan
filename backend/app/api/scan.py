import os
import json
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.scanner.main import run_scan
from app.secu.main import verify_admin # Import de ta nouvelle fonction 🛡️
from app.db import get_db_connection
from app.api.database import parse_scan_expert

router = APIRouter(prefix="/scan")

def create_pending_scan(scan_type: int) -> int:
    """Crée une entrée en base de données avec le statut 0 (en cours)"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Scan (Type, file_path, status) VALUES (%s, %s, 0)",
            (str(scan_type), "en_cours...")
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def background_scan_task(scan_type: int, scan_id: int):
    """Exécute le scan en arrière-plan et met à jour la base de données"""
    success = run_scan(scan_type)
    
    if success:
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 1. On récupère la ligne que run_scan a éventuellement insérée en base
            cursor.execute("SELECT id_scan, file_path FROM Scan WHERE Type=%s ORDER BY id_scan DESC LIMIT 1", (str(scan_type),))
            last_scan = cursor.fetchone()

            if last_scan and last_scan['id_scan'] > scan_id:
                file_path = last_scan['file_path']
                # On nettoie la ligne insérée par run_scan pour éviter les doublons
                cursor.execute("DELETE FROM Scan WHERE id_scan = %s", (last_scan['id_scan'],))
            elif last_scan:
                file_path = last_scan['file_path']
            else:
                file_path = "chemin_introuvable"

            # 2. On met à jour notre ligne initiale (passe à status = 1)
            cursor.execute("UPDATE Scan SET status = 1, file_path = %s WHERE id_scan = %s", (file_path, scan_id))
            conn.commit()

            # --- AUTOMATISATION : Remplissage de la table Vuln pour le scan complet ---
            if scan_type == 3 and file_path != "en_cours...":
                base_dir = os.path.abspath("/app/outputs") if os.name != 'nt' else os.path.abspath("outputs")
                filename = os.path.basename(file_path)
                safe_path = os.path.join(base_dir, filename)

                if os.path.exists(safe_path):
                    with open(safe_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Fetch ignored words at the time of scan
                    current_ignored_words = set()
                    temp_conn = None
                    try:
                        temp_conn = get_db_connection()
                        temp_cursor = temp_conn.cursor(dictionary=True)
                        temp_cursor.execute("SELECT text FROM liste")
                        for row in temp_cursor.fetchall():
                            current_ignored_words.add(row['text'].strip())
                    except Exception as e:
                        print(f"⚠️ Erreur récupération liste faux positifs lors du scan #{scan_id} : {e}")
                    finally:
                        if temp_conn and temp_conn.is_connected():
                            temp_cursor.close()
                            temp_conn.close()

                    vuln_results = parse_scan_expert(content)
                    vuln_results = parse_scan_expert(content, ignored_words=current_ignored_words)

                    for host in vuln_results:
                        ip = host['ip']
                        vulns_json = json.dumps(host['vulns'], ensure_ascii=False)
                        
                        cursor.execute(
                            "INSERT INTO Vuln (id_scan, hosts, text) VALUES (%s, %s, %s)",
                            (scan_id, ip, vulns_json)
                        )
                    conn.commit()

                    cursor.execute("""
                        DELETE FROM Scan 
                        WHERE DATE(Time) = CURDATE() AND Type = '3' AND id_scan != %s
                    """, (scan_id,))
                    conn.commit()
                    print(f"✅ Vulnérabilités archivées pour le scan #{scan_id}")

        except Exception as e:
            print(f"⚠️ Erreur lors de l'archivage du scan #{scan_id} : {e}")
            if conn and conn.is_connected():
                cursor.execute("UPDATE Scan SET status = -1 WHERE id_scan = %s", (scan_id,))
                conn.commit()
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    else:
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Scan SET status = -1 WHERE id_scan = %s", (scan_id,))
            conn.commit()
        except Exception:
            pass
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

@router.post("/quick")
async def scan_quick(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    """Lance un scan rapide en arrière-plan si l'utilisateur est admin 🦖"""
    scan_id = create_pending_scan(1)
    background_tasks.add_task(background_scan_task, 1, scan_id)
    return {"message": "Scan rapide lancé en arrière-plan ! ✨ Tu peux suivre l'avancée dans l'historique.", "admin": admin.get("name")}

@router.post("/security")
async def scan_security(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    """Lance un scan de sécurité en arrière-plan si l'utilisateur est admin 🛡️"""
    scan_id = create_pending_scan(2)
    background_tasks.add_task(background_scan_task, 2, scan_id)
    return {"message": "Scan sécurité lancé en arrière-plan ! ✨ Tu peux suivre l'avancée dans l'historique."}

@router.post("/full")
async def scan_full(background_tasks: BackgroundTasks, admin=Depends(verify_admin)):
    """Lance un scan complet en arrière-plan si l'utilisateur est admin 🥵"""
    scan_id = create_pending_scan(3)
    background_tasks.add_task(background_scan_task, 3, scan_id)
    return {"message": "Scan complet lancé en arrière-plan ! ✨ Tu peux suivre l'avancée dans l'historique."}