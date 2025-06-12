from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from argon2 import PasswordHasher

import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

from ai_module.password_generator import generate_password

import math

from backend.database import engine, SessionLocal
from backend.models import Base, User, PasswordVault
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

Base.metadata.create_all(bind=engine)


app = FastAPI()

# CORS middleware configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ph = PasswordHasher()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class StorePasswordRequest(BaseModel):
    email: str
    master_password: str
    site: str
    password: str | None = None  # Optional if use_ai is True
    use_ai: bool = False

class RetrievePasswordsRequest(BaseModel):
    email: str
    master_password: str

class PasswordStrengthRequest(BaseModel):
    password: str

def derive_key(master_password: str, salt: bytes) -> bytes:
    """Derives a 256-bit AES key from the master password."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return kdf.derive(master_password.encode())

def encrypt_password(password: str, key: bytes) -> dict:
    """Encrypts a password using AES-GCM."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, password.encode(), None)
    return {
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

def decrypt_password(enc_data: dict, key: bytes) -> str:
    """Decrypts a password using AES-GCM."""
    aesgcm = AESGCM(key)
    nonce = base64.b64decode(enc_data["nonce"])
    ciphertext = base64.b64decode(enc_data["ciphertext"])
    return aesgcm.decrypt(nonce, ciphertext, None).decode()

@app.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")
    hashed_password = ph.hash(req.password)
    new_user = User(email=req.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully."}

@app.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    try:
        ph.verify(user.hashed_password, req.password)
    except:
        raise HTTPException(status_code=401, detail="Incorrect password.")
    return {"message": "Login successful."}

@app.post("/store-password")
def store_password(req: StorePasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    try:
        ph.verify(user.hashed_password, req.master_password)
    except:
        raise HTTPException(status_code=401, detail="Invalid master password.")
    salt = req.email.encode()  # simple static salt for now
    key = derive_key(req.master_password, salt)
    if req.use_ai:
        password_to_store = generate_password(length=12)
    elif req.password:
        password_to_store = req.password
    else:
        raise HTTPException(status_code=400, detail="Password is required if use_ai is false.")

    enc = encrypt_password(password_to_store, key)

    vault_entry = PasswordVault(
        user_id=user.id,
        site=req.site,
        nonce=enc["nonce"],
        encrypted_password=enc["ciphertext"]
    )

    db.add(vault_entry)
    db.commit()

    return {
        "message": "Password stored securely.",
        "generated": req.use_ai,
        "password": password_to_store if req.use_ai else None
    }

@app.post("/retrieve-passwords")
def retrieve_passwords(req: RetrievePasswordsRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    try:
        ph.verify(user.hashed_password, req.master_password)
    except:
        raise HTTPException(status_code=401, detail="Invalid master password.")

    salt = req.email.encode()
    key = derive_key(req.master_password, salt)

    vault_entries = db.query(PasswordVault).filter(PasswordVault.user_id == user.id).all()
    if not vault_entries:
        return {"passwords": []}

    results = []
    for entry in vault_entries:
        enc_data = {"nonce": entry.nonce, "ciphertext": entry.encrypted_password}
        decrypted = decrypt_password(enc_data, key)
        results.append({
            "site": entry.site,
            "password": decrypted
        })
    return {"passwords": results}

@app.get("/generate-password")
def generate_password_route(
    length: int = Query(12, ge=8, le=32),
    use_symbols: bool = True
):
    password = generate_password(length, use_symbols)
    return {"password": password}

@app.post("/evaluate-strength")
def evaluate_strength(req: PasswordStrengthRequest):
    pwd = req.password
    length = len(pwd)

    # Determine character pool size
    pool = 0
    if any(c.islower() for c in pwd):
        pool += 26
    if any(c.isupper() for c in pwd):
        pool += 26
    if any(c.isdigit() for c in pwd):
        pool += 10
    if any(not c.isalnum() for c in pwd):
        pool += 32

    entropy = round(length * math.log2(pool)) if pool > 0 else 0

    # Rating scale
    if entropy < 40:
        rating = "Weak"
    elif entropy < 60:
        rating = "Moderate"
    else:
        rating = "Strong"

    return {
        "length": length,
        "character_pool_size": pool,
        "entropy_bits": entropy,
        "rating": rating
    }