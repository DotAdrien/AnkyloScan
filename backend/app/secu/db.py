import os
import mysql.connector # type: ignore

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("127.0.0.1"),
        user="root",
        password=os.getenv("ADMIN_PASSWORD"),
        database="ankyloscan"
    )