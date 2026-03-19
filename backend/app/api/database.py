import os
import re
import json # Import added for json.loads
import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Depends # Ajout de Depends 🛡️
from fastapi.responses import FileResponse
from app.secu.main import verify_admin # Import de la sécurité 🦖
from app.db import get_db_connection

router = APIRouter(prefix="/db", tags=["Database 🐬"])

@router.get("/history")
def get_scan_history(admin=Depends(verify_admin)):
    """
    Seul un admin peut consulter l'historique des scans. 🔐
    """
    conn = None
    try:
        # Connexion à la base de données 🛡️
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Récupère les 5 entrées les plus récentes 🕒
        query = """
            SELECT id_scan as id, type, Time as time, file_path, status 
            FROM Scan 
            ORDER BY Time DESC 
            LIMIT 5
        """
        cursor.execute(query)
        scans = cursor.fetchall()
        
        # Formatage des descriptions selon le type pour le front 🎨
        descriptions = {
            1: "Scan rapide terminé. ✨",
            2: "Détection des ports et adresses MAC effectuée. 👍",
            3: "Analyse complète des vulnérabilités terminée. 🦖"
        }

        descriptions_pending = {
            1: "Scan rapide en cours... ⏳",
            2: "Détection des ports et adresses MAC en cours... ⏳",
            3: "Analyse complète des vulnérabilités en cours... 🧠⏳"
        }

        for scan in scans:
            scan_type = int(scan["type"]) if scan["type"] else 1
            if scan["status"] == 0:
                scan["description"] = descriptions_pending.get(scan_type, "Scan en cours... ⏳")
            else:
                scan["description"] = descriptions.get(scan_type, "Scan effectué. 🛡️")

            if scan["time"]:
                scan["time"] = scan["time"].strftime("%d/%02m/%Y - %H:%M")

        return scans

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"La base boude : {str(e)} 😱")
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def parse_scan_expert(content, ignored_words=None):
    """
    Analyse le contenu du rapport Nmap pour extraire les vulnérabilités (Logiciel expert v3) 🧠
    """
    if ignored_words is None:
        ignored_words = set() # Default to empty set if not provided

    hosts = content.split("Nmap scan report for ")
    results = []

    for host in hosts[1:]:
        lines = host.split("\n")
        ip = lines[0].strip()
        host_vulns = []

        # 1. Scripts NSE
        nse_vulns = re.findall(r"\|\s+(.*?):\s*\n\|\s+VULNERABLE:\n\|\s+(.*?)\n\|\s+State:\s+(.*)", host)
        for script_name, title, state in nse_vulns:
            # Filtre : on ignore si le titre ou le nom du script est dans la liste (exact match)
            if script_name.strip() in ignored_words or title.strip() in ignored_words:
                continue

            level = 3 if "Exploitable" in state else 2
            host_vulns.append({
                "title": title.strip(),
                "state": state.strip(),
                "level": level,
                "badge": "🔴 [NIV 3]" if level == 3 else "🟠 [NIV 2]"
            })

        # 2. Vulners (CVE)
        vulners = re.findall(r"(CVE-\d{4}-\d+)\s+(\d+\.\d+)", host)
        for cve, score in vulners:
            # Filtre : on ignore si la CVE exacte est dans la liste
            # Ex: si cve est "CVE-520-100", elle ne sera ignorée QUE si "CVE-520-100" est dans la base
            if cve.strip() in ignored_words:
                continue

            f_score = float(score)
            if f_score >= 7.0:
                level = 3
                badge = "🔴 [NIV 3]"
            elif f_score >= 4.0:
                level = 2
                badge = "🟠 [NIV 2]"
            else:
                level = 1
                badge = "🟡 [NIV 1]"
            
            host_vulns.append({"title": f"{cve} - Score: {score}", "state": "CVE Detectée", "level": level, "badge": badge})

        # 3. Cas spécial Telnet
        if "password required but not set" in host:
            if "TELNET" not in ignored_words and "TELNET : Accès libre sans mot de passe !" not in ignored_words:
                host_vulns.append({
                    "title": "TELNET : Accès libre sans mot de passe !", 
                    "state": "Accès ouvert 🔓",
                    "level": 3, 
                    "badge": "🔴 [NIV 3]"
                })

        if len(host_vulns) > 0:
            results.append({"ip": ip, "vulns": host_vulns})
    
    return results

@router.get("/report")
def get_report_file(path: str, admin=Depends(verify_admin)):
    """
    L'accès aux fichiers de rapport est aussi protégé. 🛡️
    """
    # CORRECTION : Sécurité Directory Traversal 🛡️
    # On définit le dossier de base strict
    base_dir = os.path.abspath("/app/outputs") if os.name != 'nt' else os.path.abspath("outputs")
    # On nettoie le nom de fichier (on ne garde que le nom, pas le chemin)
    filename = os.path.basename(path)
    safe_path = os.path.join(base_dir, filename)

    # PROTECTION SUPPLÉMENTAIRE 🛡️
    # On s'assure que l'utilisateur ne télécharge QUE des rapports de scan et pas la config email/cron
    if not filename.startswith("scan_") or filename in ["email.txt", "schedule.txt"]:
        raise HTTPException(status_code=403, detail="Accès interdit à ce fichier 🚫")

    if os.path.exists(safe_path) and os.path.isfile(safe_path):
        return FileResponse(safe_path)
    raise HTTPException(status_code=404, detail="Rapport introuvable 😱")

@router.get("/vulns")
def get_vulns_analysis(path: str, admin=Depends(verify_admin)):
    """
    Retourne l'analyse experte des vulnérabilités au format JSON 🦖
    """
    base_dir = os.path.abspath("/app/outputs") if os.name != 'nt' else os.path.abspath("outputs")
    filename = os.path.basename(path)
    safe_path = os.path.join(base_dir, filename)

    if not filename.startswith("scan_") or filename in ["email.txt", "schedule.txt"]:
        raise HTTPException(status_code=403, detail="Accès interdit 🚫")

    # Restriction : Seul le scan de niveau 3 (scan_3_...) permet l'analyse de vulnérabilités
    if not filename.startswith("scan_3_"):
        raise HTTPException(status_code=400, detail="Cette analyse est réservée aux scans complets (Niveau 3).")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get id_scan from file_path
        # We need to ensure safe_path is correctly formatted for the query
        # The file_path in DB is typically '/app/outputs/scan_X_timestamp.txt'
        # safe_path is already absolute, so we need to match it.
        cursor.execute("SELECT id_scan FROM Scan WHERE file_path = %s", (safe_path,))
        scan_entry = cursor.fetchone()
        
        if not scan_entry:
            raise HTTPException(status_code=404, detail="Entrée de scan introuvable dans la base de données pour ce rapport.")
        
        scan_id = scan_entry['id_scan']
        
        # Retrieve vulnerabilities from Vuln table
        cursor.execute("SELECT hosts, text FROM Vuln WHERE id_scan = %s", (scan_id,))
        vuln_records = cursor.fetchall()
        
        results = []
        for record in vuln_records:
            results.append({
                "ip": record['hosts'],
                "vulns": json.loads(record['text']) # Parse the JSON string back to a list
            })
        
        return results

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()