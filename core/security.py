from __future__ import annotations

import hashlib
import hmac
import secrets
from uuid import uuid4

from .database import Database


class SecurityError(ValueError):
    pass


class PasswordHasher:
    ITERATIONS = 310000

    @classmethod
    def hash_password(cls, password: str) -> str:
        if not password:
            raise SecurityError("كلمة المرور مطلوبة")
        salt = secrets.token_bytes(32)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, cls.ITERATIONS)
        return f"{salt.hex()}:{digest.hex()}"

    @classmethod
    def verify_password(cls, password: str, stored_hash: str) -> bool:
        try:
            salt_hex, digest_hex = stored_hash.split(":", 1)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), cls.ITERATIONS)
            return hmac.compare_digest(actual.hex(), digest_hex)
        except (ValueError, TypeError):
            return False


class SecurityService:
    PERMISSIONS = {
        "dashboard.view", "products.view", "products.edit", "customers.view", "customers.edit",
        "suppliers.view", "suppliers.edit", "purchases.post", "sales.post", "returns.post",
        "cash.receipt", "cash.payment", "expenses.post", "accounting.view", "accounting.post",
        "reports.view", "settings.edit", "users.manage", "audit.view",
    }

    def __init__(self, db: Database):
        self.db = db
        self._ensure_schema()
        self.seed()

    def _ensure_schema(self):
        with self.db.connection() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS roles(id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL);
            CREATE TABLE IF NOT EXISTS permissions(id TEXT PRIMARY KEY, code TEXT UNIQUE NOT NULL);
            CREATE TABLE IF NOT EXISTS role_permissions(
                role_id TEXT NOT NULL, permission_id TEXT NOT NULL,
                PRIMARY KEY(role_id, permission_id),
                FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE,
                FOREIGN KEY(permission_id) REFERENCES permissions(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS users(
                id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL, role_id TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(role_id) REFERENCES roles(id)
            );
            """)

    def seed(self):
        for code in sorted(self.PERMISSIONS):
            self.db.execute("INSERT OR IGNORE INTO permissions(id,code) VALUES(?,?)", (str(uuid4()), code))
        role = self.db.fetchone("SELECT id FROM roles WHERE name='admin'")
        role_id = role["id"] if role else str(uuid4())
        if not role:
            self.db.execute("INSERT INTO roles(id,name) VALUES(?,?)", (role_id, "admin"))
        for permission in self.db.fetchall("SELECT id FROM permissions"):
            self.db.execute("INSERT OR IGNORE INTO role_permissions(role_id,permission_id) VALUES(?,?)", (role_id, permission["id"]))

    def create_role(self, name, permissions=()):
        role_id = str(uuid4())
        self.db.execute("INSERT INTO roles(id,name) VALUES(?,?)", (role_id, name.strip()))
        for code in permissions:
            p = self.db.fetchone("SELECT id FROM permissions WHERE code=?", (code,))
            if not p or code not in self.PERMISSIONS:
                raise SecurityError(f"صلاحية غير معروفة: {code}")
            self.db.execute("INSERT INTO role_permissions(role_id,permission_id) VALUES(?,?)", (role_id, p["id"]))
        return role_id

    def create_user(self, username, password, role_name="admin"):
        role = self.db.fetchone("SELECT id FROM roles WHERE name=?", (role_name,))
        if not role:
            raise SecurityError("الدور غير موجود")
        user_id = str(uuid4())
        self.db.execute(
            "INSERT INTO users(id,username,password_hash,role_id) VALUES(?,?,?,?)",
            (user_id, username.strip(), PasswordHasher.hash_password(password), role["id"]),
        )
        return user_id

    def authenticate(self, username, password):
        user = self.db.fetchone("SELECT * FROM users WHERE username=? AND active=1", (username.strip(),))
        if not user or not PasswordHasher.verify_password(password, user["password_hash"]):
            raise SecurityError("اسم المستخدم أو كلمة المرور غير صحيحة")
        return user

    def has_permission(self, user_id, permission):
        return self.db.fetchone("""
            SELECT 1 FROM users u
            JOIN role_permissions rp ON rp.role_id=u.role_id
            JOIN permissions p ON p.id=rp.permission_id
            WHERE u.id=? AND p.code=? AND u.active=1
        """, (user_id, permission)) is not None
