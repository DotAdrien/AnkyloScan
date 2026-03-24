import os
import jwt
from fastapi import HTTPException, Cookie, Depends

SECRET_KEY = os.getenv("ADMIN_PASSWORD")
ALGORITHM = "HS256"

def verify_admin(session_token: str = Cookie(None)):

    if not session_token:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    try:
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("rank") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
            
        return payload
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid session")