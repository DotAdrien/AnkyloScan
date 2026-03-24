import os
import jwt
import bcrypt
import datetime
import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, EmailStr
from app.secu.db import get_db_connection

router = APIRouter(prefix="/auth", tags=["Account 👤"])

# Récupère le MDP généré ou celui par défaut 🔑
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")
ALGORITHM = "HS256"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AdminSetup(BaseModel):
    name: str
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

@router.get("/check-init")
def check_initialization():
    """Vérifie si un admin existe déjà. Renvoie False si la base est vide (besoin de setup)."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users")
        count = cursor.fetchone()[0]
        return {"initialized": count > 0}
    except mysql.connector.Error:
        return {"initialized": True} # En cas d'erreur, on bloque le setup par sécurité
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.post("/setup")
def setup_admin(admin_data: AdminSetup):
    """Crée le PREMIER administrateur seulement si la base est vide. 🦖"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Vérification ultime : est-ce que la table est bien vide ?
        cursor.execute("SELECT COUNT(*) FROM Users")
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=403, detail="L'initialisation a déjà été effectuée ! 🚫")

        # 2. Hashage du mot de passe
        hashed_pw = bcrypt.hashpw(admin_data.password.encode('utf-8'), bcrypt.gensalt())
        
        # IMPORTANT : Décoder les bytes en string pour que MySQL le stocke proprement (sans "b'...'")
        hashed_pw_str = hashed_pw.decode('utf-8')

        # 3. Création de l'admin
        query = "INSERT INTO Users (Name, Email, Password, Role) VALUES (%s, %s, %s, 'admin')"
        cursor.execute(query, (admin_data.name, admin_data.email, hashed_pw_str))
        conn.commit()

        return {"status": "success", "message": "Administrateur créé avec succès ! Tu peux te connecter. ✨"}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

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
        
        if not user or not bcrypt.checkpw(user_data.password.encode('utf-8'), user['Password'].encode('utf-8')):
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