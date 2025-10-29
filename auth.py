from fastapi import Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
import os

SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-in-production")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

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
    except:
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
            assigned = user_obj.assigned_blocks.split(",") if user_obj.assigned_blocks else []
            if user_obj.primary_block:
                assigned.append(user_obj.primary_block)
            
            if block_name in assigned:
                return True
        
        # Fallback to session data
        user_blocks = user_data.get("blocks", "").split(",")
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
