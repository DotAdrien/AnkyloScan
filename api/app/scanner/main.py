import subprocess
# Import relatif pour la fusion 🦾
from .database_handler import save_scan_result

def run_scan(scan_type):
    configs = {
        1: ["-F", "127.0.0.1"], # Test local pour éviter les erreurs de droits 🛡️
        2: ["-sP", "127.0.0.1"],
        3: ["-sV", "127.0.0.1"]
    }
    
    args = configs.get(scan_type, configs[1])
    
    try:
        # Exécution via Nmap
        result = subprocess.run(["nmap"] + args, capture_output=True, text=True, check=True)
        save_scan_result(scan_type, result.stdout)
        return True
    except Exception as e:
        print(f"Erreur Nmap : {e} 😱")
        return False