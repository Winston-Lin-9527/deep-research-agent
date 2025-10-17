import datetime 
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os
import bcrypt

from src.database import get_db, DBUser

# Security context for password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme for API
security = HTTPBearer()

# Secret key for JWT (should be in environment variable)
SECRET_KEY = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthHandler:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_duration = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return bcrypt.checkpw(
            bytes(plain_password, 'utf-8'),
            bytes(hashed_password, 'utf-8')
        )
        
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return bcrypt.hashpw(
            bytes(password, 'utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8') # return as str

    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.timezone.utc) + self.access_token_duration
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[dict]:
        """Decode JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

# Global auth handler instance
auth_handler = AuthHandler()

# Dependency to get current user from token
async def get_current_user(
    credentials=Depends(security),
    db: Session = Depends(get_db)
):
    """Dependency to get current user from token"""
    token = credentials.credentials
    payload = auth_handler.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # actually the DB query is not necessary for authentication, but it could be used for authorization
    # or handle cases when the user account has been removed but JWT still valid (issued before revocation) 
    user = db.query(DBUser).filter(DBUser.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user_id
