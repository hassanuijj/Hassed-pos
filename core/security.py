import hashlib
import secrets


class PasswordHasher:
    ITERATIONS = 310000

    @classmethod
    def hash_password(cls, password: str) -> str:
        if not password:
            raise ValueError("كلمة المرور مطلوبة")
        salt = secrets.token_bytes(32)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, cls.ITERATIONS)
        return f"{salt.hex()}:{digest.hex()}"

    @classmethod
    def verify_password(cls, password: str, stored_hash: str) -> bool:
        try:
            salt_hex, digest_hex = stored_hash.split(":", 1)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, cls.ITERATIONS)
            return secrets.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False
