import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import mysql.connector

app = FastAPI(title="AnkyloScan API 🦖")

# Récupère le MDP généré dans le .env ou utilise celui par défaut 🔑
DB_PASSWORD = os.getenv("ADMIN_PASSWORD", "password_aleatoire")

class ScanResult(BaseModel):
    ip: str
    hostname: str = "Inconnu"
    status: str
    open_ports: List[int]

db_mock = []

@app.get("/")
def home():
    return {"message": "AnkyloScan API tournant sur le port 8001 ! 🦖🔥"}

@app.get("/test-db")
def test_db_connection():
    try:
        # Utilise les variables de ton docker-compose
        connection = mysql.connector.connect(
            host="db",
            user="admin",
            password=DB_PASSWORD,
            database="ankyloscan"
        )
        if connection.is_connected():
            connection.close()
            return {"status": "success", "message": "Connexion auto réussie ! 🛡️"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)} 😱")
