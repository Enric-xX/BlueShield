# core/auth.py
from pathlib import Path
import json
import hashlib
import base64
from cryptography.fernet import Fernet, InvalidToken
import secrets

DB_PATH = Path("shield_db.enc")

class AuthManager:
    PEPPER = b"blue-shield-elite-2026-fixed-pepper"  # Cambia esto por algo único tuyo

    @staticmethod
    def _derive_key(master_password: str) -> bytes:
        """Deriva una clave Fernet (32 bytes base64) a partir de la contraseña + pepper"""
        key_material = hashlib.scrypt(
            master_password.encode('utf-8'),
            salt=AuthManager.PEPPER,
            n=32768,        # Coste CPU/memoria
            r=8,
            p=1,
            dklen=32
        )
        return base64.urlsafe_b64encode(key_material)

    @staticmethod
    def register(username: str, master_password: str) -> bool:
        """Registra usuario → crea archivo cifrado"""
        if DB_PATH.exists():
            return False  # Ya existe → no sobreescribir

        key = AuthManager._derive_key(master_password)
        fernet = Fernet(key)

        data = {
            "username": username.strip(),
            "created": "2026-02-22",  # Puedes usar datetime.now().isoformat()
            "version": "2.6"
        }

        json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        encrypted = fernet.encrypt(json_bytes)

        DB_PATH.write_bytes(encrypted)
        return True

    @staticmethod
    def login(master_password: str) -> tuple[bool, str]:
        """Verifica contraseña → devuelve (éxito, username)"""
        if not DB_PATH.exists():
            return False, ""

        key = AuthManager._derive_key(master_password)
        fernet = Fernet(key)

        try:
            encrypted = DB_PATH.read_bytes()
            decrypted = fernet.decrypt(encrypted)
            data = json.loads(decrypted.decode('utf-8'))
            return True, data.get("username", "Usuario")
        except InvalidToken:
            return False, ""
        except Exception:
            return False, ""

    @staticmethod
    def exists() -> bool:
        return DB_PATH.exists()
