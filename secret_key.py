import secrets
import string

def generate_secret_key():
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(50))

print(generate_secret_key())