from .ngram_generator import NGramPasswordGenerator

# Load dataset once
with open("ai_module/data/passwords.txt", "r") as f:
    passwords = [line.strip() for line in f if line.strip()]

ngram_model = NGramPasswordGenerator(n=3)
ngram_model.train(passwords)

def generate_password(length=12, use_symbols=True):
    return ngram_model.generate(max_length=length, min_length=8)