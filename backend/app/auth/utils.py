from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from ..config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(subject: str, expires_minutes: int | None = None):
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALG)
