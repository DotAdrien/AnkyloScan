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

# securiser ce truc
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DB_PASSWORD = os.getenv("ADMIN_PASSWORD")

@app.get("/")
def home():
    return {
            "message": "AnkyloScan API tournant sur le port 8001 ! 🦖🔥",
        }

@app.get("/test-db")
def test_db_connection():
    try:
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
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)} 😱")


