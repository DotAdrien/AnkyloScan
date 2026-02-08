import os
import mysql.connector # type: ignore
from datetime import datetime

DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

def save_scan_result(scan_type, raw_output):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"/app/outputs/scan_{scan_type}_{timestamp}.txt"
    os.makedirs("/app/outputs", exist_ok=True)


    lines = raw_output.splitlines()
    clean_output = "\n".join([l for l in lines if "OS detection performed" not in l])

    with open(file_path, "w") as f:
        f.write(clean_output)

    try:
        conn = mysql.connector.connect(
            host="db", user="root", password=DB_PASSWORD, database="ankyloscan"
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Scan (Type, file_path) VALUES (%s, %s)", (scan_type, file_path))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erreur : {e} 😱")