import subprocess
import socket
import os
import tempfile
from .database_handler import save_scan_result
from app.api.email_sender import send_scan_report

def get_local_network():
    """Détecte le réseau de l'hôte depuis le conteneur 🌐"""
    try:
        # On cherche l'IP de la passerelle pour deviner le réseau local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        # On transforme l'IP (ex: 192.168.1.50) en réseau (192.168.1.0/24)
        return ".".join(local_ip.split('.')[:-1]) + ".0/24"
    except Exception:
        return "192.168.2.0/24" # Repli sur ton ancienne config si ça échoue 🤨

def execute_nmap_process(scan_type, args, xml_path=None):
    """Logique du scan en arrière-plan 🦾"""
    try:
        print(f"Scan {scan_type} lancé sur {args[-1]} 📷")
        result = subprocess.run(["nmap"] + args, capture_output=True, text=True, check=True)
        
        xml_output = None
        if xml_path and os.path.exists(xml_path):
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_output = f.read()

        save_scan_result(scan_type, result.stdout, xml_output)

        send_scan_report(scan_type, result.stdout)
            
        print(f"Scan {scan_type} terminé ! ✨")
    except Exception as e:
        print(f"Erreur scan {scan_type} : {e} 😱")
    finally:
        if xml_path and os.path.exists(xml_path):
            try:
                os.remove(xml_path)
            except OSError:
                pass

def run_scan(scan_type):
    """Lance le scan (FastAPI gère déjà l'exécution en arrière-plan) 🚀"""
    target_network = get_local_network()
    
    xml_path = None
    if scan_type == 3:
        fd, xml_path = tempfile.mkstemp(suffix=".xml")
        os.close(fd)
        args = ["-p-", "-T4", "-A", "--script", "vulners,vuln", "-oX", xml_path, target_network]
    elif scan_type == 2:
        args = ["-p-", "-T4", "-O", target_network]
    else:
        args = ["-O",  "-T4", target_network]
        
    # Plus besoin de thread ici, BackgroundTasks s'en occupe ! ✨
    execute_nmap_process(scan_type, args, xml_path)
    
    return True