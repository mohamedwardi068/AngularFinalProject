# auth_utils.py
import hashlib
import hmac
import time
import jwt

SECRET_KEY = "AngularProject2025HamaMita2li9"  # change before production
ALGO = "HS256"
ACCESS_TOKEN_EXPIRE = 60 * 60 * 24 * 7  # 7 days

def hash_password(password: str, salt: str):
    return hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()

def verify_password(password: str, salt: str, hashval: str):
    return hash_password(password, salt) == hashval

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE):
    payload = data.copy()
    payload.update({"exp": time.time() + expires_delta})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
    except Exception:
        return None
