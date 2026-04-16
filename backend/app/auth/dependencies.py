from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth.jwt_handler import decode_token

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token=Depends(security)):
    try:
        payload = decode_token(token.credentials)
        return payload["user_id"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")