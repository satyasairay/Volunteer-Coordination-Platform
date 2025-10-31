"""
CSRF (Cross-Site Request Forgery) protection middleware.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from itsdangerous import URLSafeTimedSerializer
import secrets
import os
import logging

logger = logging.getLogger(__name__)

# Use session secret for CSRF token signing
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-in-production")
csrf_serializer = URLSafeTimedSerializer(SESSION_SECRET)

# CSRF token expiry: 1 hour
CSRF_TOKEN_MAX_AGE = 3600


def generate_csrf_token() -> str:
    """Generate a new CSRF token"""
    token = secrets.token_urlsafe(32)
    return csrf_serializer.dumps(token)


def verify_csrf_token(token: str) -> bool:
    """Verify a CSRF token"""
    try:
        csrf_serializer.loads(token, max_age=CSRF_TOKEN_MAX_AGE)
        return True
    except Exception as e:
        logger.debug(f"CSRF token verification failed: {e}")
        return False


async def get_csrf_token(request: Request) -> str:
    """Get CSRF token from request or generate a new one"""
    # Check if token exists in session/cookies
    csrf_token = request.cookies.get("csrf_token")
    
    if not csrf_token or not verify_csrf_token(csrf_token):
        # Generate new token
        csrf_token = generate_csrf_token()
        # Store in request state to set cookie in response
        request.state.csrf_token = csrf_token
    
    return csrf_token


def validate_csrf_token(request: Request, form_token: str = None) -> bool:
    """
    Validate CSRF token from request.
    
    Args:
        request: FastAPI request object
        form_token: Optional CSRF token from form data
    
    Returns:
        True if token is valid, raises HTTPException otherwise
    """
    # Get token from form data, headers, or cookies
    token = form_token
    if not token:
        token = request.headers.get("X-CSRF-Token")
    if not token:
        token = request.cookies.get("csrf_token")
    
    if not token:
        logger.warning("CSRF token missing from request")
        raise HTTPException(
            status_code=403,
            detail="CSRF token missing. Please refresh the page and try again."
        )
    
    if not verify_csrf_token(token):
        logger.warning("Invalid or expired CSRF token")
        raise HTTPException(
            status_code=403,
            detail="Invalid or expired CSRF token. Please refresh the page and try again."
        )
    
    return True


def create_csrf_middleware(app):
    """
    Create CSRF middleware function for FastAPI app.
    This should be called during app initialization.
    """
    @app.middleware("http")
    async def csrf_middleware(request: Request, call_next):
        """
        CSRF middleware to add CSRF tokens to responses and validate on state-changing requests.
        """
        # Skip CSRF check for GET, HEAD, OPTIONS (safe methods)
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            response = await call_next(request)
            # Add CSRF token to response cookie if not present
            if not request.cookies.get("csrf_token"):
                csrf_token = generate_csrf_token()
                response.set_cookie(
                    "csrf_token",
                    csrf_token,
                    httponly=False,  # Needs to be accessible to JavaScript
                    samesite="lax",
                    max_age=CSRF_TOKEN_MAX_AGE
                )
            return response
        
        # Skip CSRF for authentication endpoints (login, register, logout)
        # These are entry points where users don't have sessions yet
        auth_paths = ["/admin/login", "/api/auth/login", "/api/auth/register", "/admin/logout"]
        if any(request.url.path == path for path in auth_paths):
            response = await call_next(request)
            # Still add CSRF token cookie if not present
            if not request.cookies.get("csrf_token"):
                csrf_token = generate_csrf_token()
                response.set_cookie(
                    "csrf_token",
                    csrf_token,
                    httponly=False,
                    samesite="lax",
                    max_age=CSRF_TOKEN_MAX_AGE
                )
            return response
        
        # For POST, PUT, DELETE, PATCH - validate CSRF token
        try:
            # Get token from form or header
            if request.method == "POST":
                try:
                    form = await request.form()
                    form_token = form.get("csrf_token")
                    validate_csrf_token(request, form_token)
                except:
                    # If form parsing fails, try header
                    validate_csrf_token(request)
            else:
                validate_csrf_token(request)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"CSRF validation error: {e}", exc_info=True)
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "CSRF validation failed"}
            )
        
        response = await call_next(request)
        return response
    
    return csrf_middleware

