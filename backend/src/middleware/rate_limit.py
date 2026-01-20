"""
Rate limiting middleware based on user_id and IP address
"""
import time
import json
from collections import defaultdict
from typing import Any, Dict, Tuple, Optional
from fastapi import Request, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from ..config.settings import settings
from ..utils.firebase_auth import verify_firebase_token


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware that tracks requests by user_id and IP address.
    Uses a sliding window approach.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.enabled = settings.rate_limit_enabled
        self.requests_per_minute = settings.rate_limit_per_minute
        # Store: {identifier: [(timestamp, ...), ...]}
        self.request_history: Dict[str, list] = defaultdict[str, list](list)
        # Cleanup interval should match the time window (1 minute = 60 seconds)
        # We track requests per minute, so cleanup every minute
        self.cleanup_interval = 60  # Clean up old entries every 60 seconds (1 minute)
        self.time_window_seconds = 60  # Time window for rate limiting (1 minute)
        self.last_cleanup = time.time()
    
    def _get_firebase_uid_from_token(self, request: Request) -> Optional[str]:
        """Extract firebase_uid from Authorization token (lightweight, no DB query)"""
        # Check if already verified and cached in request state
        if hasattr(request.state, "firebase_uid"):
            return request.state.firebase_uid
        
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None
        
        try:
            token = authorization.replace("Bearer ", "")
            decoded_token = verify_firebase_token(token)
            if not decoded_token:
                return None
            
            firebase_uid = decoded_token.get("uid")
            if firebase_uid:
                # Cache in request state for reuse by get_current_user
                request.state.firebase_uid = firebase_uid
                request.state.decoded_token = decoded_token
            return firebase_uid
        except Exception:
            # If any error occurs, just return None (don't break the request)
            return None
    
    def _get_identifier(self, request: Request) -> Tuple[Optional[str], str]:
        """Get user_id and IP identifier for rate limiting"""
        # Try to get user_id from request state (set by auth dependency)
        # This will be available if get_current_user has already run
        user_id = getattr(request.state, "user_id", None)
        
        # If not in state, use firebase_uid for rate limiting (lightweight)
        # This avoids querying DB in middleware
        if user_id is None:
            firebase_uid = self._get_firebase_uid_from_token(request)
            user_identifier = f"firebase_uid:{firebase_uid}" if firebase_uid else None
        else:
            user_identifier = f"user:{user_id}" if user_id else None
        
        # Get IP address
        client_host = request.client.host if request.client else "unknown"
        # Also check X-Forwarded-For header for proxied requests
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            client_host = forwarded_for.split(",")[0].strip()
        
        ip_identifier = f"ip:{client_host}"
        
        return user_identifier, ip_identifier
    
    def _cleanup_old_entries(self):
        """Remove entries older than the time window"""
        current_time = time.time()
        cutoff_time = current_time - self.time_window_seconds
        
        for identifier in list(self.request_history.keys()):
            # Filter out old entries
            self.request_history[identifier] = [
                ts for ts in self.request_history[identifier]
                if ts > cutoff_time
            ]
            # Remove empty entries
            if not self.request_history[identifier]:
                del self.request_history[identifier]
    
    def _check_rate_limit(self, identifier: str) -> bool:
        """Check if identifier has exceeded rate limit"""
        if not identifier:
            return True  # No identifier, skip rate limiting
        
        current_time = time.time()
        
        # Clean up old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries()
            self.last_cleanup = current_time
        
        # Get request history for this identifier
        history = self.request_history[identifier]
        
        # Remove entries older than the time window
        cutoff_time = current_time - self.time_window_seconds
        history[:] = [ts for ts in history if ts > cutoff_time]
        
        # Check if limit exceeded
        if len(history) >= self.requests_per_minute:
            return False
        
        # Add current request
        history.append(current_time)
        return True
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        # Skip rate limiting for Swagger/ReDoc endpoints
        path = request.url.path
        if path in ["/docs", "/redoc", "/openapi.json", "/"]:
            return await call_next(request)
        
        # Get identifiers
        user_identifier, ip_identifier = self._get_identifier(request)
        
        # Check rate limit for user_id (if available)
        if user_identifier:
            if not self._check_rate_limit(user_identifier):
                return Response(
                    content=json.dumps({
                        "detail": f"Rate limit exceeded for user. Maximum {self.requests_per_minute} requests per minute."
                    }),
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                    headers={
                        "X-RateLimit-Limit": str(self.requests_per_minute),
                        "X-RateLimit-Remaining": "0",
                        "Retry-After": str(self.time_window_seconds),
                    }
                )
        
        # Check rate limit for IP address
        if not self._check_rate_limit(ip_identifier):
            return Response(
                content=json.dumps({
                    "detail": f"Rate limit exceeded for IP address. Maximum {self.requests_per_minute} requests per minute."
                }),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit-IP": str(self.requests_per_minute),
                    "X-RateLimit-Remaining-IP": "0",
                    "Retry-After": str(self.time_window_seconds),
                }
            )
        
        # Continue with the request
        response = await call_next(request)
        
        # Add rate limit headers
        if user_identifier:
            remaining = self.requests_per_minute - len(self.request_history[user_identifier])
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        
        remaining_ip = self.requests_per_minute - len(self.request_history[ip_identifier])
        response.headers["X-RateLimit-Limit-IP"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-IP"] = str(max(0, remaining_ip))
        
        return response
