import os
import json
from fastapi import APIRouter, HTTPException, Depends
from app.scanner.main import run_scan
from app.secu.main import verify_admin # Import de ta nouvelle fonction 🛡️
from app.db import get_db_connection
from app.api.database import parse_scan_expert

router = APIRouter(prefix="/scan")

@router.post("/quick")
async def scan_quick(admin=Depends(verify_admin)):
    """Lance un scan rapide si l'utilisateur est admin 🦖"""
    success = run_scan(1)
    if success:
        return {"message": "Scan rapide lancé ! ✨", "admin": admin.get("name")}
    raise HTTPException(status_code=500, detail="Erreur lors du scan rapide 😱")

@router.post("/security")
async def scan_security(admin=Depends(verify_admin)):
    """Lance un scan de sécurité si l'utilisateur est admin 🛡️"""
    success = run_scan(2)
    if success:
        return {"message": "Scan sécurité lancé ! ✨"}
    raise HTTPException(status_code=500, detail="Erreur lors du scan sécurité 😱")

@router.post("/full")
async def scan_full(admin=Depends(verify_admin)):
    """Lance un scan complet si l'utilisateur est admin 🥵"""
    success = run_scan(3)
    if success:
        # --- AUTOMATISATION : Remplissage de la table Vuln ---
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 1. On récupère l'ID du scan qui vient d'être créé (le dernier scan de type 3)
            cursor.execute("SELECT id_scan, file_path FROM Scan WHERE Type='3' ORDER BY id_scan DESC LIMIT 1")
            last_scan = cursor.fetchone()

            if last_scan:
                scan_id = last_scan['id_scan']
                file_path = last_scan['file_path']

                # 2. Construction du chemin du fichier (sécurisé)
                base_dir = os.path.abspath("/app/outputs") if os.name != 'nt' else os.path.abspath("outputs")
                filename = os.path.basename(file_path)
                safe_path = os.path.join(base_dir, filename)

                # 3. Lecture et Parsing
                if os.path.exists(safe_path):
                    with open(safe_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # On utilise l'algo expert existant pour extraire les datas
                    vuln_results = parse_scan_expert(content)

                    # 4. Insertion dans la table Vuln
                    for host in vuln_results:
                        ip = host['ip']
                        # On sauvegarde la liste des failles en JSON dans la colonne text
                        vulns_json = json.dumps(host['vulns'], ensure_ascii=False)
                        
                        cursor.execute(
                            "INSERT INTO Vuln (id_scan, hosts, text) VALUES (%s, %s, %s)",
                            (scan_id, ip, vulns_json)
                        )
                    conn.commit()
                    print(f"✅ Vulnérabilités archivées pour le scan #{scan_id}")

        except Exception as e:
            print(f"⚠️ Erreur lors de l'archivage des vulnérabilités : {e}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
        # -----------------------------------------------------

        return {"message": "Scan complet lancé ! ✨"}
    raise HTTPException(status_code=500, detail="Erreur lors du scan complet 😱")