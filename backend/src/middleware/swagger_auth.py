"""
Middleware for protecting Swagger UI with basic authentication
"""
import base64
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from ..config.settings import settings


class SwaggerAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to protect Swagger UI with basic authentication"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.username = settings.swagger_username
        self.password = settings.swagger_password
    
    async def dispatch(self, request: Request, call_next):
        # Only protect Swagger/ReDoc endpoints
        path = request.url.path
        if path in ["/docs", "/redoc", "/openapi.json", "/api/docs", "/api/redoc", "/api/openapi.json"]:
            # Check for Authorization header
            authorization = request.headers.get("Authorization")
            
            if not authorization:
                return Response(
                    content="Unauthorized",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Basic"},
                )
            
            try:
                # Parse Basic Auth
                scheme, credentials = authorization.split(" ", 1)
                if scheme.lower() != "basic":
                    raise ValueError("Invalid scheme")
                
                decoded = base64.b64decode(credentials).decode("utf-8")
                username, password = decoded.split(":", 1)
                
                # Verify credentials
                if username != self.username or password != self.password:
                    return Response(
                        content="Unauthorized",
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        headers={"WWW-Authenticate": "Basic"},
                    )
            except (ValueError, IndexError):
                return Response(
                    content="Unauthorized",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Basic"},
                )
        
        # Continue with the request
        response = await call_next(request)
        return response
