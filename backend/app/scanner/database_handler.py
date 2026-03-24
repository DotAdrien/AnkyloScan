import os
from datetime import datetime
from app.secu.db import get_db_connection

def save_scan_result(scan_type, raw_output, xml_output=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"/app/outputs/scan_{scan_type}_{timestamp}.txt"
    os.makedirs("/app/outputs", exist_ok=True)


    lines = raw_output.splitlines()
    clean_output = "\n".join([l for l in lines if "OS detection performed" not in l])

    with open(file_path, "w") as f:
        f.write(clean_output)
        
    if xml_output:
        xml_path = file_path.replace(".txt", ".xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_output)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Scan (Type, file_path) VALUES (%s, %s)", (scan_type, file_path))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erreur : {e} 😱")