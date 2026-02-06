import subprocess
import threading
from .database_handler import save_scan_result
from .email_sender import send_email_report

def execute_nmap_process(scan_type, args):
    """Logique du scan exécutée en arrière-plan 🦾"""
    try:
        # Le scan peut prendre du temps, mais il tourne sur son propre thread 🧵
        result = subprocess.run(["nmap"] + args, capture_output=True, text=True, check=True)
        save_scan_result(scan_type, result.stdout)

        # Envoi de l'email si c'est un Scan Rapide 📧
        if scan_type == 1:
            send_email_report(result.stdout)
            
        print(f"Scan {scan_type} terminé avec succès ! ✨")
    except Exception as e:
        print(f"Erreur lors du scan {scan_type} : {e} 😱")

def run_scan(scan_type):
    """Lance le scan sans bloquer l'application 🚀"""
    configs = {
        1: ["-O", "127.0.0.1"],
        2: ["-p-", "-O", "127.0.0.1"],
        3: ["-p-", "-A", "--script", "vuln", "127.0.0.1"]
    }
    
    args = configs.get(scan_type, configs[1])
    
    # Création d'un thread dédié pour ce scan 🧠
    scan_thread = threading.Thread(target=execute_nmap_process, args=(scan_type, args))
    scan_thread.daemon = True  # Le thread meurt si le serveur s'arrête
    scan_thread.start()
    
    # On retourne True immédiatement pour libérer l'API 🌷
    return True