import subprocess
# Remplace la ligne 2 par :
from .database_handler import save_scan_result

def run_scan(scan_type):
    # Définition des arguments selon le type de scan
    configs = {
        1: ["-F", "-O", "192.168.1.0/24"],
        2: ["-sP", "192.168.1.0/24"],
        3: ["-sV", "--script", "vuln", "192.168.1.0/24"]
    }
    
    args = configs.get(scan_type, configs[1])
    
    try:
        # Exécution du scan 🚀
        result = subprocess.run(["nmap"] + args, capture_output=True, text=True, check=True)
        # Envoi au deuxième fichier pour traitement
        save_scan_result(scan_type, result.stdout)
        return True
    except Exception as e:
        print(f"Erreur lors du scan : {e} 😱")
        return False

if __name__ == "__main__":
    # Test rapide
    run_scan(1)