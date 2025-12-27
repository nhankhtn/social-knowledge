"""
Firebase authentication utilities
"""
import firebase_admin
from firebase_admin import auth, credentials
from typing import Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_firebase_app: Optional[firebase_admin.App] = None

def init_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app

    try:
        # Try to load firebase_config.json from project root
        config_path = Path(__file__).parent.parent.parent / "firebase_config.json"
        
        if config_path.exists():
            logger.info(f"Loading Firebase config from {config_path}")
            cred = credentials.Certificate(str(config_path))
            _firebase_app = firebase_admin.initialize_app(cred)
        else:
            logger.error("Firebase config file not found at expected location %s", config_path)
            raise FileNotFoundError("firebase_config.json not found")        
        
        logger.info("Firebase Admin SDK initialized")
        return _firebase_app
    except Exception as e:
        logger.warning(f"Firebase Admin SDK initialization failed: {e}")
        logger.warning("Token verification will be skipped. Make sure to set GOOGLE_APPLICATION_CREDENTIALS or add firebase_config.json")
        return None

def verify_firebase_token(token: str) -> Optional[dict]:
    """
    Verify Firebase ID token
    
    Returns:
        Decoded token claims if valid, None otherwise
    """
    global _firebase_app
    
    if _firebase_app is None:
        # Try to initialize if not already done
        init_firebase()
    
    if _firebase_app is None:
        logger.warning("Firebase not initialized, skipping token verification")
        # For development, you might want to return None or raise an error
        return None
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None

