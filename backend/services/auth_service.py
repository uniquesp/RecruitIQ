import jwt
import bcrypt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..database.crud import user_crud
from ..database.connection import get_database
from ..models.schemas import User, RegisterRequest

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return JWT token"""
        db = next(get_database())
        try:
            user = user_crud.get_user_by_email(db, email)
            
            if not user or not self._verify_password(password, user.hashed_password):
                raise Exception("Invalid credentials")
            
            # Generate JWT token
            access_token = self._create_access_token(
                data={"sub": user.email, "user_id": user.id, "role": user.role}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role
                }
            }
        finally:
            db.close()
    
    async def create_user(self, request: RegisterRequest) -> Dict[str, Any]:
        """Create new user account"""
        db = next(get_database())
        try:
            # Check if user already exists
            existing_user = user_crud.get_user_by_email(db, request.email)
            if existing_user:
                raise Exception("User already exists")
            
            # Hash password
            hashed_password = self._hash_password(request.password)
            
            # Create user in database
            user = user_crud.create_user(db, request, hashed_password)
            
            # Generate token
            access_token = self._create_access_token(
                data={"sub": user.email, "user_id": user.id, "role": user.role}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role
                }
            }
        finally:
            db.close()
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get current user from JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise Exception("Invalid token")
            
            db = next(get_database())
            try:
                user = user_crud.get_user_by_email(db, email)
                if user is None:
                    raise Exception("User not found")
                
                return {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role
                }
            finally:
                db.close()
        except jwt.PyJWTError:
            raise Exception("Invalid token")
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
