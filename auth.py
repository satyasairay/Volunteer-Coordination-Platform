from fastapi import Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired, BadData
from passlib.context import CryptContext
import os
import logging
import warnings

# Configure logging
logger = logging.getLogger(__name__)

# Environment variable validation - require credentials in production
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

SESSION_SECRET = os.getenv("SESSION_SECRET")
if not SESSION_SECRET:
    if ENVIRONMENT == "production":
        raise ValueError("SESSION_SECRET must be set in production environment")
    SESSION_SECRET = "dev-secret-change-in-production"
    warnings.warn("Using default SESSION_SECRET - DO NOT USE IN PRODUCTION", UserWarning)
    logger.warning("Using default SESSION_SECRET - DO NOT USE IN PRODUCTION")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
if not ADMIN_EMAIL:
    if ENVIRONMENT == "production":
        raise ValueError("ADMIN_EMAIL must be set in production environment")
    ADMIN_EMAIL = "admin@example.com"
    warnings.warn("Using default ADMIN_EMAIL - DO NOT USE IN PRODUCTION", UserWarning)
    logger.warning("Using default ADMIN_EMAIL - DO NOT USE IN PRODUCTION")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    if ENVIRONMENT == "production":
        raise ValueError("ADMIN_PASSWORD must be set in production environment")
    ADMIN_PASSWORD = "admin123"
    warnings.warn("Using default ADMIN_PASSWORD - DO NOT USE IN PRODUCTION", UserWarning)
    logger.warning("Using default ADMIN_PASSWORD - DO NOT USE IN PRODUCTION")

serializer = URLSafeTimedSerializer(SESSION_SECRET)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt (12 rounds)"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_session_token(email: str, role: str = "super_admin") -> str:
    """Create a session token with email and role"""
    return serializer.dumps({"email": email, "role": role})


def verify_session_token(token: str) -> dict | None:
    """Verify and decode session token (7-day expiry)"""
    try:
        return serializer.loads(token, max_age=86400 * 7)
    except (BadSignature, SignatureExpired, BadData) as e:
        # Expected errors for invalid/expired tokens
        logger.debug(f"Session token verification failed: {type(e).__name__}")
        return None
    except Exception as e:
        # Log unexpected errors for debugging
        logger.error(f"Unexpected error in verify_session_token: {e}", exc_info=True)
        return None


def get_current_admin(request: Request):
    """Legacy admin check - for backward compatibility"""
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    data = verify_session_token(token)
    if not data or data.get("role") != "super_admin":
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return data


def get_current_user(request: Request) -> dict:
    """Get current authenticated user from session (any role)"""
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    data = verify_session_token(token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return data


def get_optional_user(request: Request) -> dict | None:
    """Get current user if logged in, None otherwise (for public pages)"""
    token = request.cookies.get("session")
    if not token:
        return None
    
    data = verify_session_token(token)
    return data if data else None


def require_role(allowed_roles: list[str]):
    """Dependency to check if user has required role"""
    def role_checker(request: Request):
        user = get_current_user(request)
        role = user.get("role")
        
        if role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        
        return user
    
    return role_checker


def require_super_admin(request: Request):
    """Dependency for super admin only routes"""
    user = get_current_user(request)
    if user.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    return user


def require_block_coordinator(request: Request):
    """Dependency for block coordinator routes"""
    user = get_current_user(request)
    if user.get("role") not in ["super_admin", "block_coordinator"]:
        raise HTTPException(status_code=403, detail="Block coordinator access required")
    return user


def check_block_access(user_data: dict, block_name: str, user_obj = None) -> bool:
    """
    Check if user has access to a specific block
    Args:
        user_data: Session data with role and blocks
        block_name: Name of the block to check
        user_obj: Optional User database object for assigned_blocks
    Returns:
        True if user has access, raises HTTPException otherwise
    """
    role = user_data.get("role")
    
    # Super admin has access to all blocks
    if role == "super_admin":
        return True
    
    # Block coordinator - check assigned blocks
    if role == "block_coordinator":
        if user_obj:
            # Check assigned_blocks from database
            assigned = []
            if user_obj.assigned_blocks:
                assigned = [b.strip() for b in user_obj.assigned_blocks.split(",") if b.strip()]
            if user_obj.primary_block:
                assigned.append(user_obj.primary_block)
            
            if block_name in assigned:
                return True
        
        # Fallback to session data
        user_blocks_str = user_data.get("blocks") or ""
        user_blocks = [b.strip() for b in user_blocks_str.split(",") if b.strip()] if user_blocks_str else []
        if block_name in user_blocks:
            return True
    
    raise HTTPException(
        status_code=403,
        detail=f"You do not have access to {block_name} block"
    )


def require_admin(request: Request):
    """Legacy function - redirects to login"""
    try:
        return get_current_admin(request)
    except HTTPException:
        raise HTTPException(status_code=303, detail="Redirect to login", headers={"Location": "/admin/login"})
