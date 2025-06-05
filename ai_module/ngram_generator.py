import random
from collections import defaultdict

class NGramPasswordGenerator:
    def __init__(self, n=3):
        self.n = n
        self.model = defaultdict(list)

    def train(self, password_list):
        for pwd in password_list:
            padded = "~" * (self.n - 1) + pwd + "~"
            for i in range(len(padded) - self.n + 1):
                prefix = padded[i:i + self.n - 1]
                next_char = padded[i + self.n - 1]
                self.model[prefix].append(next_char)

    def generate(self, max_length=12, min_length=8):
        prefix = "~" * (self.n - 1)
        result = ""
        max_attempts = 100
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            next_chars = self.model.get(prefix, ["~"])
            next_char = random.choice(next_chars)
            if next_char == "~":
                if len(result) >= min_length:
                    break  # Allow end only if minimum length is reached
                else:
                    continue  # Keep generating characters

            if len(result) >= max_length:
                break
            result += next_char
            prefix = prefix[1:] + next_char

        if attempts == max_attempts:
            print("⚠️  Password generation hit max attempts. Returning partial result.")
        return result