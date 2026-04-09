from cryptography.fernet import Fernet
from src.core.config import ENCRYPTION_KEY

_fernet = Fernet(ENCRYPTION_KEY.encode('utf-8'))

def encrypt_key(raw_key: str) -> str:
    """
    Encrypts a plaintext API key for database storage.
    
    @Architecture-Map: [CORE-SEC-AUTH]
    @Docs: docs/reference/07_ARCHITECTURE_MAP.md
    """
    return _fernet.encrypt(raw_key.encode('utf-8')).decode('utf-8')

def decrypt_key(encrypted_key: str) -> str:
    """Decrypts an encrypted API key back to plaintext for API calls."""
    return _fernet.decrypt(encrypted_key.encode('utf-8')).decode('utf-8')
