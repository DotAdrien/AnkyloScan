import os
import mysql.connector # type: ignore
from datetime import datetime

# Récupération du mot de passe via l'environnement
DB_PASSWORD = os.getenv("ADMIN_PASSWORD", "password_aleatoire")

def save_scan_result(scan_type, raw_output):
    # 1. Création du fichier output.txt avec un nom unique 📄
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"scan_type{scan_type}_{timestamp}.txt"
    file_path = f"/app/outputs/{file_name}"
    
    os.makedirs("/app/outputs", exist_ok=True)
    with open(file_path, "w") as f:
        f.write(raw_output)

    # 2. Ajout dans la base de données 🛡️
    try:
        conn = mysql.connector.connect(
            host="db",
            user="root",
            password=DB_PASSWORD,
            database="ankyloscan"
        )
        cursor = conn.cursor()
        
        # On insère le type et le chemin du fichier
        query = "INSERT INTO Scan (Type, file_path) VALUES (%s, %s)"
        cursor.execute(query, (scan_type, file_path))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Données enregistrées avec succès ! ✨")
    except Exception as e:
        print(f"Erreur base de données : {e} 😱")