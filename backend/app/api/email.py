import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/email", tags=["Email 📧"])


EMAIL_FILE = "/app/outputs/email.txt"

class EmailConfig(BaseModel):
    sender: EmailStr
    api_key: str
    receivers: str

@router.post("/save")
async def save_email_config(config: EmailConfig):
    try:
        with open(EMAIL_FILE, "w") as f:
            f.write(f"{config.sender}\n")
            f.write(f"{config.api_key}\n")
            f.write(f"{config.receivers}")
            
        return {"status": "success", "message": "Configuration enregistrée ! 🦖✨"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture : {str(e)} 😱")