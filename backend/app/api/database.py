import os
import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Depends # Ajout de Depends 🛡️
from fastapi.responses import FileResponse
from app.secu.main import verify_admin # Import de la sécurité 🦖

router = APIRouter(prefix="/db", tags=["Database 🐬"])

# Récupère le mot de passe depuis l'environnement 🔑
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

@router.get("/history")
def get_scan_history(admin=Depends(verify_admin)):
    """
    Seul un admin peut consulter l'historique des scans. 🔐
    """
    conn = None
    try:
        # Connexion à la base de données 🛡️
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password=DB_PASSWORD,
            database="ankyloscan"
        )
        cursor = conn.cursor(dictionary=True)
        
        # Récupère les 5 entrées les plus récentes 🕒
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
            scan["description"] = descriptions.get(scan["type"], "Scan effectué. 🛡️")
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
def get_report_file(path: str, admin=Depends(verify_admin)):
    """
    L'accès aux fichiers de rapport est aussi protégé. 🛡️
    """
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="Rapport introuvable 😱")