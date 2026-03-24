import os
import jwt
import bcrypt
import datetime
import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, EmailStr
from app.secu.db import get_db_connection

router = APIRouter(prefix="/auth", tags=["Account 👤"])

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
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users")
        count = cursor.fetchone()[0]
        return {"initialized": count > 0}
    except mysql.connector.Error:
        return {"initialized": True}
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.post("/setup")
def setup_admin(admin_data: AdminSetup):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Users")
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=403, detail="Initialization has already been completed! 🚫")

        hashed_pw = bcrypt.hashpw(admin_data.password.encode('utf-8'), bcrypt.gensalt())
        hashed_pw_str = hashed_pw.decode('utf-8')

        query = "INSERT INTO Users (Name, Email, Password, Role) VALUES (%s, %s, %s, 'admin')"
        cursor.execute(query, (admin_data.name, admin_data.email, hashed_pw_str))
        conn.commit()

        return {"status": "success", "message": "Administrator created successfully! You can now log in. ✨"}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"SQL Error: {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.post("/login")
def login(user_data: UserLogin, response: Response):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT id_users, Name, Email, Role, Password FROM Users WHERE Email=%s"
        cursor.execute(query, (user_data.email,))
        user = cursor.fetchone()
        
        if not user or not bcrypt.checkpw(user_data.password.encode('utf-8'), user['Password'].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Incorrect email or password ❌")

        token = create_jwt(user)
        
        response.set_cookie(
            key="session_token", 
            value=token, 
            httponly=False, 
            samesite="lax"
        )
        
        return {
            "status": "success", 
            "token": token,
            "message": f"Welcome back {user['Name']}! 🦖✨"
        }

    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database connection error... 😱")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()