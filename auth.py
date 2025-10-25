from fastapi import Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer
import os

SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-in-production")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

serializer = URLSafeTimedSerializer(SESSION_SECRET)


def create_session_token(email: str) -> str:
    return serializer.dumps({"email": email})


def verify_session_token(token: str) -> dict:
    try:
        return serializer.loads(token, max_age=86400 * 7)
    except:
        return None


def get_current_admin(request: Request):
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    data = verify_session_token(token)
    if not data or data.get("email") != ADMIN_EMAIL:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return data


def require_admin(request: Request):
    try:
        return get_current_admin(request)
    except HTTPException:
        raise HTTPException(status_code=303, detail="Redirect to login", headers={"Location": "/admin/login"})
