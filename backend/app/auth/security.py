from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.database import get_db
from app.models.models import User
pwd=CryptContext(schemes=["bcrypt"], deprecated="auto"); bearer=HTTPBearer()
def hash_password(p:str): return pwd.hash(p)
def verify_password(p:str,h:str): return pwd.verify(p,h)
def create_token(user_id:str):
 s=get_settings(); return jwt.encode({"sub":user_id,"exp":datetime.now(timezone.utc)+timedelta(minutes=s.jwt_expire_minutes)},s.jwt_secret,algorithm="HS256")
def current_user(credentials:HTTPAuthorizationCredentials=Depends(bearer), db:Session=Depends(get_db)):
 try: uid=jwt.decode(credentials.credentials,get_settings().jwt_secret,algorithms=["HS256"])["sub"]
 except (JWTError,KeyError): raise HTTPException(status_code=401,detail="Invalid authentication token")
 user=db.get(User,uid)
 if not user: raise HTTPException(status_code=401,detail="User not found")
 return user
def make_api_key(env_key:str):
 raw=f"ff_{env_key}_{secrets.token_urlsafe(32)}"; return raw,sha256(raw.encode()).hexdigest()
def key_hash(raw:str): return sha256(raw.encode()).hexdigest()
