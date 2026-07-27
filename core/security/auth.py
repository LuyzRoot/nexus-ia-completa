"""Security policies and access control"""
import logging
from typing import Optional, List
from datetime import datetime, timedelta
import jwt

from config.settings import settings

logger = logging.getLogger(__name__)


class TokenManager:
    """JWT token management"""

    @staticmethod
    def create_token(
        user_id: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create JWT token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        
        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        
        return token

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            user_id = payload.get("user_id")
            return user_id
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None


class RBACManager:
    """Role-Based Access Control manager"""

    ROLES = {
        "admin": ["read", "write", "delete", "manage_users"],
        "user": ["read", "write"],
        "guest": ["read"],
    }

    @staticmethod
    def has_permission(user_role: str, required_permission: str) -> bool:
        """Check if user role has required permission"""
        permissions = RBACManager.ROLES.get(user_role, [])
        return required_permission in permissions

    @staticmethod
    def get_permissions(user_role: str) -> List[str]:
        """Get all permissions for a role"""
        return RBACManager.ROLES.get(user_role, [])
