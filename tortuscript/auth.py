"""Server-side session primitives for adult accounts."""
import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

SESSION_HOURS = 12


def _now():
    return datetime.now(timezone.utc)


def _iso(value):
    return value.isoformat(timespec="seconds")


def _digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class AuthError(ValueError):
    pass


class AuthRepository:
    def __init__(self, path):
        self.path = Path(path)

    def _db(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def ensure_schema(self):
        with self._db() as db:
            cols = {row["name"] for row in db.execute("PRAGMA table_info(accounts)")}
            if "password_hash" not in cols:
                db.execute("ALTER TABLE accounts ADD COLUMN password_hash TEXT")
            if "verified_at" not in cols:
                db.execute("ALTER TABLE accounts ADD COLUMN verified_at TEXT")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id_hash TEXT PRIMARY KEY,
                    account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                    csrf_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    revoked_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_sessions_account ON sessions(account_id);
            """)


    def marcar_verificada(self, account_id):
        with self._db() as db:
            row = db.execute("SELECT 1 FROM accounts WHERE id=?", (account_id,)).fetchone()
            if not row:
                raise AuthError("La cuenta no existe.")
            db.execute(
                "UPDATE accounts SET verified_at=? WHERE id=?",
                (_iso(_now()), account_id),
            )

    def set_password(self, account_id, password):
        if not isinstance(password, str) or len(password) < 12:
            raise AuthError("La contraseña debe tener al menos 12 caracteres.")
        encoded = generate_password_hash(password, method="scrypt")
        with self._db() as db:
            db.execute("UPDATE accounts SET password_hash=? WHERE id=?", (encoded, account_id))

    def verify_password(self, email, password):
        email = (email or "").strip().lower()
        with self._db() as db:
            row = db.execute(
                "SELECT id,email,password_hash,verified_at,role FROM accounts WHERE email=?",
                (email,),
            ).fetchone()
        if not row or not row["password_hash"] or not check_password_hash(row["password_hash"], password or ""):
            raise AuthError("Correo o contraseña incorrectos.")
        if not row["verified_at"]:
            raise AuthError("La cuenta todavía no verificó su correo.")
        return row

    def create_session(self, account_id):
        session = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(32)
        now = _now()
        expires = now + timedelta(hours=SESSION_HOURS)
        with self._db() as db:
            db.execute(
                "INSERT INTO sessions VALUES (?,?,?,?,?,NULL)",
                (_digest(session), account_id, _digest(csrf), _iso(now), _iso(expires)),
            )
        return session, csrf, expires

    def get_session(self, session):
        if not session:
            return None
        with self._db() as db:
            row = db.execute(
                "SELECT * FROM sessions WHERE id_hash=?",
                (_digest(session),),
            ).fetchone()
        if not row or row["revoked_at"]:
            return None
        if datetime.fromisoformat(row["expires_at"]) <= _now():
            return None
        return row

    def csrf_ok(self, session, csrf):
        row = self.get_session(session)
        return bool(row and csrf and hmac.compare_digest(row["csrf_hash"], _digest(csrf)))

    def revoke(self, session):
        if not session:
            return
        with self._db() as db:
            db.execute(
                "UPDATE sessions SET revoked_at=? WHERE id_hash=?",
                (_iso(_now()), _digest(session)),
            )
