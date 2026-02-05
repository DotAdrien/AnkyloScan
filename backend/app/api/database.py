import os
import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/db", tags=["Database 🐬"])

# Récupère le mot de passe depuis l'environnement 🔑
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

@router.get("/history")
def get_scan_history():
    conn = None
    try:
        # Connexion à la base de données 🛡️
        conn = mysql.connector.connect(
            host="db",
            user="root",
            password=DB_PASSWORD,
            database="ankyloscan"
        )
        cursor = conn.cursor(dictionary=True)
        
        # Récupère les 5 entrées les plus récentes via l'ID ou le Time 🕒
        query = """
            SELECT id_scan as id, type, Time as time, file_path 
            FROM Scan 
            ORDER BY Time DESC 
            LIMIT 5
        """
        cursor.execute(query)
        scans = cursor.fetchall()
        
        # Formatage des descriptions selon le type pour le front 🎨
        descriptions = {
            1: "Scan rapide terminé. ✨",
            2: "Détection des ports et adresses MAC effectuée. 👍",
            3: "Analyse complète des vulnérabilités terminée. 🦖"
        }

        for scan in scans:
            # On ajoute une description lisible si elle n'est pas en base
            scan["description"] = descriptions.get(scan["type"], "Scan effectué. 🛡️")
            # Conversion du datetime en string pour le JSON
            if scan["time"]:
                scan["time"] = scan["time"].strftime("%d/%02m/%Y - %H:%M")

        return scans

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"La base boude : {str(e)} 😱")
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.get("/report")
def get_report_file(path: str):
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="Rapport introuvable 😱")