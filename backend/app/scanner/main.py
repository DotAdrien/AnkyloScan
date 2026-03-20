import subprocess
import socket
from .database_handler import save_scan_result
from .email_sender import send_email_report

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

def execute_nmap_process(scan_type, args):
    """Logique du scan en arrière-plan 🦾"""
    try:
        print(f"Scan {scan_type} lancé sur {args[-1]} 📷")
        result = subprocess.run(["nmap"] + args, capture_output=True, text=True, check=True)
        save_scan_result(scan_type, result.stdout)

        if scan_type == 3:
            send_email_report(result.stdout)
            
        print(f"Scan {scan_type} terminé ! ✨")
    except Exception as e:
        print(f"Erreur scan {scan_type} : {e} 😱")

def run_scan(scan_type):
    """Lance le scan (FastAPI gère déjà l'exécution en arrière-plan) 🚀"""
    target_network = get_local_network()
    
    configs = {
        1: ["-O",  "-T4",                           target_network],
        2: ["-p-", "-T4", "-O",                     target_network],
        3: ["-p-", "-T4", "-A", "--script", "vuln", target_network]
    }
    
    args = configs.get(scan_type, configs[1])
    
    # Plus besoin de thread ici, BackgroundTasks s'en occupe ! ✨
    execute_nmap_process(scan_type, args)
    
    return True