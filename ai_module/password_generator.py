import random
import string

def generate_password(length=12, use_symbols=True):
    chars = string.ascii_letters + string.digits
    if use_symbols:
        chars += "!@#$%^&*()"

    password = ''.join(random.choice(chars) for _ in range(length))
    return password