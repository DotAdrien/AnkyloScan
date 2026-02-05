import os
import mysql.connector # type: ignore
from datetime import datetime

DB_PASSWORD = os.getenv("ADMIN_PASSWORD", "password_aleatoire")

def save_scan_result(scan_type, raw_output):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"scan_type{scan_type}_{timestamp}.txt"
    # Le chemin /app/outputs correspond au volume Docker 🐳
    file_path = f"/app/outputs/{file_name}"
    
    os.makedirs("/app/outputs", exist_ok=True)
    with open(file_path, "w") as f:
        f.write(raw_output)

    try:
        conn = mysql.connector.connect(
            host="db",
            user="root",
            password=DB_PASSWORD,
            database="ankyloscan"
        )
        cursor = conn.cursor()
        # Attention : 'Type' avec une majuscule pour matcher ton init.sql 🐬
        query = "INSERT INTO Scan (Type, file_path) VALUES (%s, %s)"
        cursor.execute(query, (scan_type, file_path))
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur SQL : {e} 😱")