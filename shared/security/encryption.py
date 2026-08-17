"""
Шифрование токенов и чувствительных данных
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class TokenEncryptor:
    """Шифрование токенов доступа"""
    
    def __init__(self, encryption_key: str):
        """
        Инициализация шифровальщика
        
        Args:
            encryption_key: Ключ шифрования (минимум 32 байта)
        """
        if len(encryption_key) < 32:
            raise ValueError("Ключ шифрования должен быть не менее 32 байт")
        
        # Генерация ключа Fernet из master-ключа
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'personal_planner_salt_v1',  # В продакшене использовать уникальный salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
        self.fernet = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """Шифрование строки"""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Расшифровка строки"""
        decoded = base64.urlsafe_b64decode(ciphertext.encode())
        decrypted = self.fernet.decrypt(decoded)
        return decrypted.decode()
    
    def encrypt_dict(self, data: dict) -> dict:
        """Шифрование словаря с токенами"""
        encrypted = {}
        for key, value in data.items():
            if 'token' in key.lower() or 'secret' in key.lower() or 'password' in key.lower():
                encrypted[key] = self.encrypt(str(value))
            else:
                encrypted[key] = value
        return encrypted
    
    def decrypt_dict(self, data: dict) -> dict:
        """Расшифровка словаря с токенами"""
        decrypted = {}
        for key, value in data.items():
            if 'token' in key.lower() or 'secret' in key.lower() or 'password' in key.lower():
                try:
                    decrypted[key] = self.decrypt(value)
                except Exception:
                    decrypted[key] = value  # Если не зашифровано, оставляем как есть
            else:
                decrypted[key] = value
        return decrypted


def generate_encryption_key() -> str:
    """Генерация случайного ключа шифрования"""
    return base64.urlsafe_b64encode(os.urandom(32)).decode()


# Глобальный экземпляр (инициализируется в runtime)
_encryptor = None


def get_encryptor(encryption_key: str) -> TokenEncryptor:
    """Получение экземпляра шифровальщика"""
    global _encryptor
    if _encryptor is None:
        _encryptor = TokenEncryptor(encryption_key)
    return _encryptor


def encrypt_token(token: str, encryption_key: str) -> str:
    """Удобная функция для шифрования токена"""
    encryptor = TokenEncryptor(encryption_key)
    return encryptor.encrypt(token)


def decrypt_token(ciphertext: str, encryption_key: str) -> str:
    """Удобная функция для расшифровки токена"""
    encryptor = TokenEncryptor(encryption_key)
    return encryptor.decrypt(ciphertext)
