import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/email", tags=["Email 📧"])

# Chemin vers le fichier de configuration
EMAIL_FILE = "/app/outputs/email.txt"

class EmailConfig(BaseModel):
    sender: EmailStr
    api_key: str
    receivers: str

@router.post("/save")
async def save_email_config(config: EmailConfig):
    try:
        # Création du dossier si inexistant
        os.makedirs(os.path.dirname(EMAIL_FILE), exist_ok=True)
        
        # Écriture des 3 lignes demandées 📝
        with open(EMAIL_FILE, "w") as f:
            f.write(f"{config.sender}\n")
            f.write(f"{config.api_key}\n")
            f.write(f"{config.receivers}")
            
        return {"status": "success", "message": "Configuration enregistrée ! 🦖✨"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture : {str(e)} 😱")