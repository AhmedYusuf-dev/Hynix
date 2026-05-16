from cryptography.fernet import Fernet
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Secure Key Generation
# In production, the MASTER_KEY should be in an environment variable or hardware vault
MASTER_KEY_SECRET = os.getenv("HYNIX_VAULT_SECRET", "default_secure_passphrase_change_me")
SALT = b'hynix_salt_fixed' # In high security, use a unique salt per user/deployment

def get_vault_key():
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(MASTER_KEY_SECRET.encode()))
    return key

cipher_suite = Fernet(get_vault_key())

def encrypt_data(data: str) -> str:
    """Encrypts a string using AES-256 (Fernet)."""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypts a string using AES-256 (Fernet)."""
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

if __name__ == "__main__":
    test_str = "Hynix 1 Mini Top Secret Reasoning"
    encrypted = encrypt_data(test_str)
    decrypted = decrypt_data(encrypted)
    print(f"Original: {test_str}")
    print(f"Encrypted: {encrypted[:20]}...")
    print(f"Decrypted: {decrypted}")
    assert test_str == decrypted
