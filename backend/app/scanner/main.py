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
        print(f"Scan {scan_type} lancé sur {args[-1]} 📷", flush=True)
        
        # Utilisation de Popen pour lire la sortie Nmap en temps réel ✨
        process = subprocess.Popen(["nmap"] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        output_lines = []
        for line in process.stdout:
            output_lines.append(line)
            # On affiche les lignes contenant les statistiques de progression dans la console Python
            if "Stats:" in line or "About" in line:
                print(f"⏳ [Scan {scan_type}] Progression : {line.strip()}", flush=True)
                
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
        
        xml_output = None
        if xml_path and os.path.exists(xml_path):
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_output = f.read()

        raw_output = "".join(output_lines)
        save_scan_result(scan_type, raw_output, xml_output)

        send_scan_report(scan_type, raw_output)
            
        print(f"Scan {scan_type} terminé ! ✨", flush=True)
    except Exception as e:
        print(f"Erreur scan {scan_type} : {e} 😱", flush=True)
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
        args = ["-p-", "-T4", "-sV", "--script", "vulners,vuln", "-oX", xml_path, target_network]
    elif scan_type == 2:
        args = ["-p-", "-T4", "-O", target_network]
    else:
        args = ["-O",  "-T4", target_network]
        
    # Plus besoin de thread ici, BackgroundTasks s'en occupe ! ✨
    execute_nmap_process(scan_type, args, xml_path)
    
    return True