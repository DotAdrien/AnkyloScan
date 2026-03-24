import os
import json
from app.scanner.main import run_scan
from app.secu.db import get_db_connection
from app.api.email_sender import send_vuln_alert

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

def parse_scan_expert(content, ignored_words=None):
    """
    Analyse le contenu du rapport Nmap (format XML) pour extraire les vulnérabilités 🧠
    Structure : Hôte -> Port -> Vulnérabilités
    """
    if ignored_words is None:
        ignored_words = set()

    import xml.etree.ElementTree as ET
    
    results = []
    
    try:
        root = ET.fromstring(content)
    except Exception:
        return results
        
    for host in root.findall("host"):
        address_elem = host.find("address[@addrtype='ipv4']")
        if address_elem is None:
            continue
        ip = address_elem.get("addr")
        
        host_ports = []
        
        ports_elem = host.find("ports")
        if ports_elem is not None:
            for port in ports_elem.findall("port"):
                port_id = port.get("portid")
                port_vulns = []
                
                for script in port.findall("script"):
                    script_id = script.get("id")
                    output = script.get("output")
                    
                    if script_id == "vulners":
                        for cpe_table in script.findall("table"):
                            for vuln_table in cpe_table.findall("table"):
                                vuln_id = ""
                                cvss = 0.0
                                is_exploit = False
                                for elem in vuln_table.findall("elem"):
                                    if elem.get("key") == "id":
                                        vuln_id = elem.text
                                    elif elem.get("key") == "cvss":
                                        try:
                                            cvss = float(elem.text)
                                        except (ValueError, TypeError):
                                            pass
                                    elif elem.get("key") == "is_exploit":
                                        is_exploit = (elem.text == "true")
                                        
                                if vuln_id:
                                    if vuln_id.strip() in ignored_words:
                                        continue
                                        
                                    level = 1
                                    badge = "🟡 [NIV 1]"
                                    if cvss >= 7.0 or is_exploit:
                                        level = 3
                                        badge = "🔴 [NIV 3]"
                                    elif cvss >= 4.0:
                                        level = 2
                                        badge = "🟠 [NIV 2]"
                                        
                                    port_vulns.append({
                                        "title": f"{vuln_id} - Score: {cvss}",
                                        "state": "CVE Detectée",
                                        "level": level,
                                        "badge": badge
                                    })
                    elif script_id and ("vuln" in script_id or script_id.startswith("ssl-")):
                        found_table = False
                        for table in script.findall("table"):
                            title_elem = table.find("elem[@key='title']")
                            state_elem = table.find("elem[@key='state']")
                            if title_elem is not None and state_elem is not None:
                                title = title_elem.text
                                state = state_elem.text
                                found_table = True
                                
                                if title.strip() in ignored_words or script_id.strip() in ignored_words:
                                    continue
                                    
                                level = 3 if "EXPLOITABLE" in state.upper() or "VULNERABLE" in state.upper() else 2
                                badge = "🔴 [NIV 3]" if level == 3 else "🟠 [NIV 2]"
                                
                                port_vulns.append({
                                    "title": title.strip(),
                                    "state": state.strip(),
                                    "level": level,
                                    "badge": badge
                                })
                        
                        if not found_table and output and "VULNERABLE" in output:
                            if script_id.strip() not in ignored_words:
                                port_vulns.append({
                                    "title": script_id,
                                    "state": "VULNERABLE",
                                    "level": 3,
                                    "badge": "🔴 [NIV 3]"
                                })

                    # 3. Cas spécial Telnet
                    if output and "password required but not set" in output:
                        if "TELNET" not in ignored_words and "TELNET : Accès libre sans mot de passe !" not in ignored_words:
                            port_vulns.append({
                                "title": "TELNET : Accès libre sans mot de passe !", 
                                "state": "Accès ouvert 🔓",
                                "level": 3, 
                                "badge": "🔴 [NIV 3]"
                            })
                            
                if len(port_vulns) > 0:
                    host_ports.append({
                        "port": port_id,
                        "vulns": port_vulns
                    })
                    
        if len(host_ports) > 0:
            results.append({
                "ip": ip,
                "ports": host_ports
            })
    
    return results

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
                filename = os.path.basename(file_path).replace(".txt", ".xml")
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

                    vuln_results = parse_scan_expert(content, ignored_words=current_ignored_words)

                    for host in vuln_results:
                        ip = host['ip']
                        vulns_json = json.dumps(host['ports'], ensure_ascii=False)
                        
                        cursor.execute(
                            "INSERT INTO Vuln (id_scan, hosts, text) VALUES (%s, %s, %s)",
                            (scan_id, ip, vulns_json)
                        )
                    conn.commit()
                    print(f"✅ Vulnérabilités archivées pour le scan #{scan_id}")

                    # --- ENVOI D'EMAIL POUR LES VULNÉRABILITÉS DE NIVEAU 3 ---
                    send_vuln_alert(scan_id, file_path, vuln_results)

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