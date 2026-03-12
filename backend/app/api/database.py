import os
import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Depends # Ajout de Depends 🛡️
from fastapi.responses import FileResponse
from app.secu.main import verify_admin # Import de la sécurité 🦖
from app.db import get_db_connection

router = APIRouter(prefix="/db", tags=["Database 🐬"])

@router.get("/history")
def get_scan_history(admin=Depends(verify_admin)):
    """
    Seul un admin peut consulter l'historique des scans. 🔐
    """
    conn = None
    try:
        # Connexion à la base de données 🛡️
        conn = get_db_connection()
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
    # CORRECTION : Sécurité Directory Traversal 🛡️
    # On définit le dossier de base strict
    base_dir = os.path.abspath("/app/outputs") if os.name != 'nt' else os.path.abspath("outputs")
    # On nettoie le nom de fichier (on ne garde que le nom, pas le chemin)
    filename = os.path.basename(path)
    safe_path = os.path.join(base_dir, filename)

    # PROTECTION SUPPLÉMENTAIRE 🛡️
    # On s'assure que l'utilisateur ne télécharge QUE des rapports de scan et pas la config email/cron
    if not filename.startswith("scan_") or filename in ["email.txt", "schedule.txt"]:
        raise HTTPException(status_code=403, detail="Accès interdit à ce fichier 🚫")

    if os.path.exists(safe_path) and os.path.isfile(safe_path):
        return FileResponse(safe_path)
    raise HTTPException(status_code=404, detail="Rapport introuvable 😱")