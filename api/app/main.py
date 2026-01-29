import os
from fastapi import FastAPI, HTTPException
import mysql.connector # type: ignore
from app.account import router as auth_router

app = FastAPI(title="AnkyloScan API 🦖")

# Récupère le MDP généré ou celui par défaut 🔑
DB_PASSWORD = os.getenv("ADMIN_PASSWORD", "password_aleatoire")

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

# Inclusion des routes du fichier account.py 🔌
app.include_router(auth_router)