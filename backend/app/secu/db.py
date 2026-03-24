import os
import mysql.connector # type: ignore

def get_db_connection():
    """Crée une connexion centralisée à la base de données 🐬"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user="root",
        password=os.getenv("ADMIN_PASSWORD"),
        database="ankyloscan"
    )