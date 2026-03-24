import mysql.connector # type: ignore
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.secu.main import verify_admin
from app.secu.db import get_db_connection

router = APIRouter(prefix="/liste", tags=["Liste 📝"])

class WordCreate(BaseModel):
    text: str

@router.get("/")
def get_words(admin=Depends(verify_admin)):
    """Récupère tous les mots de la liste en DB."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, text FROM liste ORDER BY id ASC")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur DB : {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.post("/")
def add_word(word: WordCreate, admin=Depends(verify_admin)):
    """Ajoute un nouveau mot dans la base de données."""
    if not word.text.strip():
        raise HTTPException(status_code=400, detail="Le mot ne peut pas être vide.")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO liste (text) VALUES (%s)", (word.text.strip(),))
        conn.commit()
        new_id = cursor.lastrowid
        return {"status": "success", "id": new_id, "text": word.text.strip(), "message": "Mot ajouté ! ✨"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur DB : {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@router.delete("/{word_id}")
def delete_word(word_id: int, admin=Depends(verify_admin)):
    """Supprime un mot de la base de données via son ID."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM liste WHERE id = %s", (word_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Mot introuvable.")
        return {"status": "success", "message": "Mot supprimé ! 🗑️"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur DB : {str(e)}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()