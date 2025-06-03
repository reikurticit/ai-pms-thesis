import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import random
import string
import json

# Endpoint
url = "http://127.0.0.1:8000/evaluate-strength"

# --- Load real passwords ---
with open("ai_module/data/passwords.txt", "r") as f:
    real_passwords = [line.strip() for line in f if len(line.strip()) >= 8]

# --- AI-generated passwords ---
from ai_module.password_generator import generate_password
ai_passwords = [generate_password(length=12) for _ in range(50)]
print("✅ AI passwords generated.")

# --- Random passwords ---
def random_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

random_passwords = [random_password(12) for _ in range(50)]
print("✅ Random passwords generated.")

# --- User passwords (sampled from file) ---
user_passwords = random.sample(real_passwords, 50)
print("✅ User passwords sampled.")

# --- Helper: evaluate via API ---
def evaluate(pwd):
    r = requests.post(url, json={"password": pwd})
    return r.json()

# --- Evaluate all ---
results = []

for category, pwds in [
    ("AI", ai_passwords),
    ("Random", random_passwords),
    ("User", user_passwords),
]:
    for pwd in pwds:
        data = evaluate(pwd)
        results.append({
            "category": category,
            "password": pwd,
            **data
        })

print("✅ Evaluation complete.")

# --- Save to JSON file ---
with open("password_strength_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("✅ Evaluation complete. Results saved to password_strength_results.json")