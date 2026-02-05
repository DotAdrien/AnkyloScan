import os
import jwt
import datetime
import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Account 👤"])

# Récupère le MDP généré ou celui par défaut 🔑
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")
ALGORITHM = "HS256"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

def create_jwt(user):
    """Génère un token contenant l'ID, le nom, l'email et le rang 🔑"""
    payload = {
        "user_id": user["id_users"],
        "name": user["Name"],
        "email": user["Email"],
        "rank": user["Role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, DB_PASSWORD, algorithm=ALGORITHM)

@router.post("/login")
def login(user_data: UserLogin, response: Response):
    conn = None
    try:
        # Connexion au service 'db' défini dans docker-compose
        conn = mysql.connector.connect(
            host="db", 
            user="root", 
            password=DB_PASSWORD, 
            database="ankyloscan"
        )
        cursor = conn.cursor(dictionary=True)
        
        # Vérification en base avec récupération de toutes les infos
        query = "SELECT id_users, Name, Email, Role FROM Users WHERE Email=%s AND Password=%s"
        cursor.execute(query, (user_data.email, user_data.password))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect ❌")

        # Création du token enrichi
        token = create_jwt(user)
        
        # httponly=False est CRUCIAL ici pour que ton JS puisse lire le profil tout seul 🍪
        response.set_cookie(
            key="session_token", 
            value=token, 
            httponly=False, 
            samesite="lax"
        )
        
        return {
            "status": "success", 
            "token": token,
            "message": f"Content de te revoir {user['Name']} ! 🦖✨"
        }

    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="La base de données boude... 😱")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()