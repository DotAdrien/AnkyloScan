import os
import jwt
from fastapi import HTTPException, Cookie, Depends

# Récupération de la clé secrète générée à l'install 🔑
SECRET_KEY = os.getenv("ADMIN_PASSWORD")
ALGORITHM = "HS256"

def verify_admin(session_token: str = Cookie(None)):

    if not session_token:
        raise HTTPException(status_code=401, detail="Non connecté 😶")
    
    try:
        # Décodage du token avec la clé du .env
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=[ALGORITHM])
        

        if payload.get("rank") != "admin":
            raise HTTPException(status_code=403, detail="Accès réservé aux admins ! 🚫")
            
        return payload
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Session invalide 😱")