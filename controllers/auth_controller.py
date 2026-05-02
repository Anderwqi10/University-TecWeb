import hashlib
import secrets
import time

from sqlalchemy.orm import Session

from core.auth import create_access_token, hash_password, verify_password
from models.db_user_model import User as UserDB
from models.user_model import LoginRequest, UserCreate, VerifyEmailRequest
from services.mailer import send_verification_email


class AuthController:
    CODE_TTL_SECONDS = 10 * 60

    @staticmethod
    def _hash_code(email: str, code: str) -> str:
        raw = f"{email.lower()}:{code}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _generate_code() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def register(user: UserCreate, db: Session) -> UserDB:
        existing = db.query(UserDB).filter(UserDB.email == str(user.email)).first()
        code = AuthController._generate_code()
        expires_at = int(time.time()) + AuthController.CODE_TTL_SECONDS
        code_hash = AuthController._hash_code(str(user.email), code)

        if existing:
            if getattr(existing, "is_verified", False):
                raise ValueError("EMAIL_ALREADY_VERIFIED")

            existing.hashed_password = hash_password(user.password)
            existing.verification_code_hash = code_hash
            existing.verification_code_expires_at = expires_at
            db.commit()
            db.refresh(existing)

            # 🔥 MODO DEV
            try:
                send_verification_email(to_email=str(user.email), code=code)
            except Exception as e:
                print("⚠️ Error enviando correo:", e)
                print(f"🔥 OTP PARA {user.email}: {code}")

            return existing

        new_user = UserDB(
            email=str(user.email),
            hashed_password=hash_password(user.password),
            is_verified=False,
            verification_code_hash=code_hash,
            verification_code_expires_at=expires_at,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 🔥 MODO DEV
        try:
            send_verification_email(to_email=str(user.email), code=code)
        except Exception as e:
            print("⚠️ Error enviando correo:", e)
            print(f"🔥 OTP PARA {user.email}: {code}")

        return new_user

    @staticmethod
    def login(payload: LoginRequest, db: Session) -> str:
        user = db.query(UserDB).filter(UserDB.email == str(payload.email)).first()
        if not user:
            raise ValueError("INVALID_CREDENTIALS")

        if not getattr(user, "is_verified", False):
            raise ValueError("EMAIL_NOT_VERIFIED")

        if not verify_password(payload.password, user.hashed_password):
            raise ValueError("INVALID_CREDENTIALS")

        return create_access_token(subject=str(user.email))

    @staticmethod
    def verify_email(payload: VerifyEmailRequest, db: Session) -> UserDB:
        user = db.query(UserDB).filter(UserDB.email == str(payload.email)).first()
        if not user:
            raise ValueError("INVALID_CODE")

        if getattr(user, "is_verified", False):
            return user

        now = int(time.time())
        exp = getattr(user, "verification_code_expires_at", None)
        if not exp or now > int(exp):
            raise ValueError("CODE_EXPIRED")

        expected = getattr(user, "verification_code_hash", None)
        if not expected:
            raise ValueError("INVALID_CODE")

        code = "".join(ch for ch in payload.code if ch.isdigit())
        if len(code) != 6 or AuthController._hash_code(str(payload.email), code) != expected:
            raise ValueError("INVALID_CODE")

        user.is_verified = True
        user.verification_code_hash = None
        user.verification_code_expires_at = None
        db.commit()
        db.refresh(user)
        return user