import os
from fastapi import APIRouter, HTTPException, Depends # Ajout de Depends 🛡️
from pydantic import BaseModel, EmailStr
from app.secu.main import verify_admin # Import de la sécurité 🦖

router = APIRouter(prefix="/email", tags=["Email 📧"])

EMAIL_FILE = "/app/outputs/email.txt"

class EmailConfig(BaseModel):
    sender: EmailStr
    api_key: str
    receivers: str

@router.post("/save")
async def save_email_config(config: EmailConfig, admin=Depends(verify_admin)):
    """
    Seul un admin peut modifier les paramètres d'alerte. 🔐
    Le token est vérifié avant d'écrire sur le disque.
    """
    try:
        with open(EMAIL_FILE, "w") as f:
            f.write(f"{config.sender}\n")
            f.write(f"{config.api_key}\n")
            f.write(f"{config.receivers}")
            
        return {
            "status": "success", 
            "message": f"Config enregistrée par {admin.get('name')} ! 🦖✨"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture : {str(e)} 😱")