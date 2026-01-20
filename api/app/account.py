from fastapi import APIRouter, HTTPException, Response, Cookie
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Account 👤"])

# Modèles
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Simulation de base de données 🐱
FAKE_DB_USER = {
    "id": 1,
    "nom": "Dot",
    "prenom": "Adrien",
    "pseudo": "DotAdrien",
    "email": "admin@ankyloscan.com",
    "role": "admin"
}

@router.post("/login")
def login(user_data: UserLogin, response: Response):
    # Tigrounet vérifie tes accès 🔑
    if user_data.email == FAKE_DB_USER["email"]:
        response.set_cookie(key="session_token", value="secure_token_xyz", httponly=True)
        return {"status": "success", "message": "Content de te revoir ! 🥰"}
    raise HTTPException(status_code=401, detail="Accès refusé ❌")

@router.get("/me")
def get_me(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token != "secure_token_xyz":
        raise HTTPException(status_code=403, detail="Tu n'es pas connecté 😱")
    return FAKE_DB_USER

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session_token")
    return {"message": "Déconnecté, à plus ! 👋"}