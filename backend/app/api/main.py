import os
from fastapi import FastAPI, HTTPException
import mysql.connector # type: ignore
from fastapi.middleware.cors import CORSMiddleware





app = FastAPI(title="AnkyloScan API 🦖")


from app.api.account import router as auth_router
from app.api.scan import router as scan_router
from app.api.database import router as db_router
from app.api.email import router as email_router
from app.api.planificateur import router as plan_router

app.include_router(auth_router)
app.include_router(scan_router)
app.include_router(db_router)
app.include_router(email_router)
app.include_router(plan_router)

# Fichier : backend/app/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Autorise toutes les IPs à se connecter 🌐
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Récupère le MDP généré ou celui par défaut 🔑
DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

@app.get("/")
def home():
    return {
            "message": "AnkyloScan API tournant sur le port 8001 ! 🦖🔥", 
            "password_debug": DB_PASSWORD  # Ajoute une clé ici ✨
        }

@app.get("/test-db")
def test_db_connection():
    try:
        # Connexion au service 'db' défini dans docker-compose
        connection = mysql.connector.connect(
            host="db",
            user="root",
            password=DB_PASSWORD,
            database="ankyloscan"
        )
        if connection.is_connected():
            connection.close()
            return {"status": "success", "message": "Connexion réussie ! 🛡️"}
    except Exception as e:
        # Tigrounet signale une erreur si la base boude 😱
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)} 😱")


