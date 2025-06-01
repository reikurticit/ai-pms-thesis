from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from argon2 import PasswordHasher

import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

from ai_module.password_generator import generate_password


app = FastAPI()
ph = PasswordHasher()

# In-memory "user database"
# {email: [list of password entries]}
users_db = {}
vault_db = {}  

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
    password: str

class RetrievePasswordsRequest(BaseModel):
    email: str
    master_password: str

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
def register(req: RegisterRequest):
    if req.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists.")
    hashed_password = ph.hash(req.password)
    users_db[req.email] = hashed_password
    return {"message": "User registered successfully."}

@app.post("/login")
def login(req: LoginRequest):
    if req.email not in users_db:
        raise HTTPException(status_code=401, detail="User not found.")
    try:
        ph.verify(users_db[req.email], req.password)
    except:
        raise HTTPException(status_code=401, detail="Incorrect password.")
    return {"message": "Login successful."}

@app.post("/store-password")
def store_password(req: StorePasswordRequest):
    if req.email not in users_db:
        raise HTTPException(status_code=401, detail="User not found.")
    # Verify the password (optional)
    try:
        ph.verify(users_db[req.email], req.master_password)
    except:
        raise HTTPException(status_code=401, detail="Invalid master password.")
    salt = req.email.encode()  # simple static salt for now
    key = derive_key(req.master_password, salt)
    enc = encrypt_password(req.password, key)

    vault_entry = {
        "site": req.site,
        "encrypted_password": enc
    }

    if req.email not in vault_db:
        vault_db[req.email] = []
    vault_db[req.email].append(vault_entry)

    return {"message": "Password stored securely."}

@app.post("/retrieve-passwords")
def retrieve_passwords(req: RetrievePasswordsRequest):
    if req.email not in users_db:
        raise HTTPException(status_code=401, detail="User not found.")
    try:
        ph.verify(users_db[req.email], req.master_password)
    except:
        raise HTTPException(status_code=401, detail="Invalid master password.")

    salt = req.email.encode()
    key = derive_key(req.master_password, salt)

    if req.email not in vault_db:
        return {"passwords": []}

    results = []
    for entry in vault_db[req.email]:
        decrypted = decrypt_password(entry["encrypted_password"], key)
        results.append({
            "site": entry["site"],
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