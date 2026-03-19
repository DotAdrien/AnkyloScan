import os
import json
from fastapi import APIRouter, HTTPException, Depends # Ajout de Depends 🛡️
from pydantic import BaseModel, EmailStr
from app.secu.main import verify_admin # Import de la sécurité 🦖

router = APIRouter(prefix="/email", tags=["Email 📧"])

EMAIL_FILE = "/app/outputs/email_config.json" # Changement de nom pour le fichier JSON

class EmailConfig(BaseModel):
    sender_email: EmailStr
    api_key: str
    recipients: str
    vuln_level3_alerts: bool = False
    agent_log_alerts: bool = False

@router.get("/config")
async def get_email_config(admin=Depends(verify_admin)):
    """
    Récupère la configuration email actuelle depuis le fichier.
    """
    if not os.path.exists(EMAIL_FILE):
        # Retourne une configuration par défaut si le fichier n'existe pas
        return EmailConfig(
            sender_email="",
            api_key="",
            recipients="",
            vuln_level3_alerts=False,
            agent_log_alerts=False
        )
    
    try:
        with open(EMAIL_FILE, "r") as f:
            config_data = json.load(f)
        return EmailConfig(**config_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de lecture du fichier de configuration email (JSON invalide) 😱")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de lecture du fichier de configuration email : {str(e)} 😱")

@router.post("/save")
async def save_email_config(config: EmailConfig, admin=Depends(verify_admin)):
    """
    Seul un admin peut modifier les paramètres d'alerte. 🔐
    Le token est vérifié avant d'écrire sur le disque. Les données sont sauvegardées en JSON.
    """
    try:
        os.makedirs(os.path.dirname(EMAIL_FILE), exist_ok=True)
        with open(EMAIL_FILE, "w") as f:
            json.dump(config.dict(), f, indent=4)
            
        return {
            "status": "success", 
            "message": f"Config enregistrée par {admin.get('name')} ! 🦖✨"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture du fichier de configuration email : {str(e)} 😱")