import subprocess
from .database_handler import save_scan_result
from .email_sender import send_email_report # Nouvel import 🧠

def run_scan(scan_type):
    configs = {
        1: ["-F", "127.0.0.1"],
        2: ["-sP", "127.0.0.1"],
        3: ["-sV", "127.0.0.1"]
    }
    
    args = configs.get(scan_type, configs[1])
    
    try:
        result = subprocess.run(["nmap"] + args, capture_output=True, text=True, check=True)
        save_scan_result(scan_type, result.stdout)

        # Si c'est un Scan Rapide (Type 1), on envoie l'email 📧🔥
        if scan_type == 1:
            send_email_report(result.stdout)

        return True
    except Exception as e:
        print(f"Erreur Nmap : {e} 😱")
        return False