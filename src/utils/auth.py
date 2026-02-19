import hashlib
import hmac
import json
import time
import base64
import logging
import os
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Roles hierarchy: admin > reviewer > analyst
ROLE_HIERARCHY = {
    "admin": 3,
    "reviewer": 2,
    "analyst": 1,
}

# Default users (in production, these would be in a database)
DEFAULT_USERS = {
    "admin": {
        "password_hash": None,  # Set at runtime from env
        "role": "admin",
        "name": "Administrator",
    },
    "analyst_01": {
        "password_hash": None,
        "role": "analyst",
        "name": "Analyst One",
    },
    "reviewer_01": {
        "password_hash": None,
        "role": "reviewer",
        "name": "Reviewer One",
    },
}


def _hash_password(password: str, salt: str = "auditwatch") -> str:
    """Hash a password using SHA-256 with salt."""
    salted = f"{salt}:{password}"
    return hashlib.sha256(salted.encode("utf-8")).hexdigest()


def _get_jwt_secret() -> str:
    """Get JWT secret from environment."""
    return os.getenv("JWT_SECRET", "default-jwt-secret-change-in-production")


def _b64_encode(data: bytes) -> str:
    """URL-safe base64 encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64_decode(data: str) -> bytes:
    """URL-safe base64 decode with padding restoration."""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode("utf-8"))


class AuthManager:
    """JWT-based authentication with role-based access control.

    Implements HS256 JWT tokens using only Python stdlib (no PyJWT dependency).
    Three roles: analyst, reviewer, admin.
    """

    def __init__(self):
        self.secret = _get_jwt_secret()
        self.token_expiry_hours = 24
        self._init_users()

    def _init_users(self):
        """Initialize default users with hashed passwords."""
        admin_password = os.getenv("ADMIN_PASSWORD", "auditwatch2026")

        DEFAULT_USERS["admin"]["password_hash"] = _hash_password(admin_password)
        DEFAULT_USERS["analyst_01"]["password_hash"] = _hash_password("analyst123")
        DEFAULT_USERS["reviewer_01"]["password_hash"] = _hash_password("reviewer123")

        self.users = DEFAULT_USERS.copy()

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token if valid."""
        user = self.users.get(username)
        if not user:
            logger.warning("Authentication failed: unknown user '%s'", username)
            return None

        password_hash = _hash_password(password)
        if password_hash != user["password_hash"]:
            logger.warning("Authentication failed: invalid password for '%s'", username)
            return None

        token = self.create_token(username, user["role"])
        logger.info("User '%s' authenticated successfully (role: %s)", username, user["role"])
        return token

    def create_token(self, user_id: str, role: str) -> str:
        """Create a JWT token (HS256, stdlib only)."""
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": user_id,
            "role": role,
            "iat": int(time.time()),
            "exp": int(time.time()) + (self.token_expiry_hours * 3600),
        }

        header_b64 = _b64_encode(json.dumps(header).encode("utf-8"))
        payload_b64 = _b64_encode(json.dumps(payload).encode("utf-8"))

        signing_input = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self.secret.encode("utf-8"),
            signing_input.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        signature_b64 = _b64_encode(signature)

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify a JWT token and return claims if valid."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature_b64 = parts

            # Verify signature
            signing_input = f"{header_b64}.{payload_b64}"
            expected_sig = hmac.new(
                self.secret.encode("utf-8"),
                signing_input.encode("utf-8"),
                hashlib.sha256,
            ).digest()
            actual_sig = _b64_decode(signature_b64)

            if not hmac.compare_digest(expected_sig, actual_sig):
                logger.warning("Token verification failed: invalid signature")
                return None

            # Decode payload
            payload = json.loads(_b64_decode(payload_b64).decode("utf-8"))

            # Check expiry
            if payload.get("exp", 0) < time.time():
                logger.warning("Token expired for user '%s'", payload.get("sub"))
                return None

            return payload

        except Exception as e:
            logger.error("Token verification error: %s", e)
            return None

    def check_role(self, token: str, required_role: str) -> bool:
        """Check if token has the required role or higher."""
        claims = self.verify_token(token)
        if not claims:
            return False

        user_role = claims.get("role", "")
        user_level = ROLE_HIERARCHY.get(user_role, 0)
        required_level = ROLE_HIERARCHY.get(required_role, 0)

        return user_level >= required_level

    def get_user_info(self, token: str) -> Optional[Dict]:
        """Get user information from token."""
        claims = self.verify_token(token)
        if not claims:
            return None

        user_id = claims.get("sub", "")
        user_data = self.users.get(user_id, {})

        return {
            "user_id": user_id,
            "role": claims.get("role", "unknown"),
            "name": user_data.get("name", user_id),
        }
