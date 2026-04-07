import os
import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.secu.main import verify_admin

router = APIRouter(prefix="/email", tags=["Email 📧"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAIL_FILE = os.path.join(BASE_DIR, "outputs", "email_config.json")

class EmailConfig(BaseModel):
    sender_email: str
    api_key: str
    recipients: str
    scan_quick_alerts: bool = False
    scan_security_alerts: bool = False
    scan_full_alerts: bool = False
    agent_log_alerts: bool = False

@router.get("/config")
async def get_email_config(admin=Depends(verify_admin)):
    if not os.path.exists(EMAIL_FILE):
        return EmailConfig(
            sender_email="",
            api_key="",
            recipients="",
            scan_quick_alerts=False,
            scan_security_alerts=False,
            scan_full_alerts=False,
            agent_log_alerts=False
        )
    
    try:
        with open(EMAIL_FILE, "r") as f:
            config_data = json.load(f)
        return EmailConfig(**config_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error reading email configuration file (Invalid JSON) 😱")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading email configuration file: {str(e)} 😱")

@router.post("/save")
async def save_email_config(config: EmailConfig, admin=Depends(verify_admin)):
    try:
        os.makedirs(os.path.dirname(EMAIL_FILE), exist_ok=True)
        with open(EMAIL_FILE, "w") as f:
            json.dump(config.dict(), f, indent=4)
            
        return {
            "status": "success", 
            "message": f"Configuration saved by {admin.get('name')}! 🦖✨"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing email configuration file: {str(e)} 😱")