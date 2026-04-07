import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.secu.main import verify_admin
from app.secu.db import get_db_connection

router = APIRouter(prefix="/liste", tags=["List 📝"])

class IgnoreCreate(BaseModel):
    host: str
    port: str

@router.get("/")
def get_ignored(admin=Depends(verify_admin)):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, host, port FROM liste ORDER BY id ASC")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.post("/")
def add_ignored(ignored: IgnoreCreate, admin=Depends(verify_admin)):
    if not ignored.host.strip() or not ignored.port.strip():
        raise HTTPException(status_code=400, detail="Host and port cannot be empty.")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO liste (host, port) VALUES (%s, %s)", (ignored.host.strip(), ignored.port.strip()))
        conn.commit()
        new_id = cursor.lastrowid
        return {"status": "success", "id": new_id, "host": ignored.host.strip(), "port": ignored.port.strip(), "message": "Ignored rule added! ✨"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.delete("/{word_id}")
def delete_ignored(word_id: int, admin=Depends(verify_admin)):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM liste WHERE id = %s", (word_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rule not found.")
        return {"status": "success", "message": "Rule deleted! 🗑️"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()