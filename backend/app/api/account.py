import os
import jwt
import bcrypt
import datetime
import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, EmailStr
from app.db import get_db_connection

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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Vérification en base avec récupération de toutes les infos
        # On récupère le hash du mot de passe pour le vérifier avec bcrypt
        query = "SELECT id_users, Name, Email, Role, Password FROM Users WHERE Email=%s"
        cursor.execute(query, (user_data.email,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect ❌")

        # LOGIQUE DE MIGRATION AUTOMATIQUE (Cleartext -> Bcrypt) 🔄
        password_valid = False
        try:
            # 1. On essaie de vérifier comme un hash Bcrypt
            if bcrypt.checkpw(user_data.password.encode('utf-8'), user['Password'].encode('utf-8')):
                password_valid = True
        except ValueError:
            # 2. Si ça plante (Invalid Salt), c'est que c'est un vieux mot de passe en clair
            if user_data.password == user['Password']:
                password_valid = True
                # 3. On le met à jour immédiatement en version hachée pour la prochaine fois 🛡️
                new_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("UPDATE Users SET Password=%s WHERE id_users=%s", (new_hash, user['id_users']))
                conn.commit()

        if not password_valid:
             raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect ❌")

        # Création du token enrichi
        token = create_jwt(user)
        
        # httponly=False est CRUCIAL ici pour que ton JS puisse lire le profil tout seul 🍪
        response.set_cookie(
            key="session_token", 
            value=token, 
            httponly=True, 
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