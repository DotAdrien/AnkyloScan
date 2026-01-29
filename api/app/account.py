import jwt
import datetime
from fastapi import APIRouter, HTTPException, Response, Cookie, Depends
from pydantic import BaseModel, EmailStr
import mysql.connector


router = APIRouter(prefix="/auth", tags=["Account 👤"])

DB_PASSWORD = os.getenv("ADMIN_PASSWORD", "password_aleatoire")
ALGORITHM = "HS256"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Fonction pour créer le token 🎟️
def create_jwt(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, DB_PASSWORD, algorithm=ALGORITHM)

@router.post("/login")
def login(user_data: UserLogin, response: Response):
    try:
        conn = mysql.connector.connect(host="db", user="admin", password=DB_PASSWORD, database="ankyloscan")
        cursor = conn.cursor(dictionary=True)
        
        # Vérification en base 🔍
        cursor.execute("SELECT ID, Email FROM Users WHERE Email=%s AND Password=%s", (user_data.email, user_data.password))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect ❌")

        token = create_jwt(user["ID"])
        response.set_cookie(key="session_token", value=token, httponly=True)
        
        return {"status": "success", "token": token} # On renvoie aussi le token au cas où
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@router.get("/me")
def get_me(session_token: str = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=403, detail="Pas de cookie 😱")
    
    try:
        # On décode le token pour retrouver l'ID 🕵️‍♂️
        payload = jwt.decode(session_token, DB_PASSWORD, algorithms=[ALGORITHM])
        return {"user_id": payload["user_id"], "message": "Tu es bien là ! 🥰"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expirée 😪")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide 🤨")

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session_token")
    return {"message": "Déconnecté, à plus ! 👋"}

@router.post("/setup-admin")
def create_admin():
    try:
        # Connexion à la base de données ankyloscan 🛡️
        connection = mysql.connector.connect(
            host="db",
            user="admin",
            password=DB_PASSWORD,
            database="ankyloscan"
        )
        cursor = connection.cursor()

        # Requête pour insérer l'admin spécifique 👤
        sql = "INSERT INTO Users (Name, Email, Password, Role) VALUES (%s, %s, %s, %s)"
        val = ("admin", "admin@gmail.com", "admin", "admin")
        
        cursor.execute(sql, val)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return {"status": "success", "message": "Admin ajouté à la base ! 🥵✨"}
    except Exception as e:
        # Tigrounet signale une erreur si la base boude 😱
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {str(e)}")