import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import json
import logging

# Configure logging to see errors in Render logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_firebase():
    """Initializes the Firebase Admin SDK from file OR environment variable."""
    if not firebase_admin._apps:
        # 1. OPTION A: Check if the JSON is in an Environment Variable (for Render)
        env_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        
        if env_json:
            try:
                logger.info("Attempting to initialize Firebase via Environment Variable...")
                # Parse the JSON string from the environment variable
                cred_dict = json.loads(env_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                logger.info("Successfully initialized Firebase via Environment Variable.")
            except Exception as e:
                logger.error(f"Error parsing FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
                # Fallback to default
                firebase_admin.initialize_app()
        else:
            # 2. OPTION B: Look for the local file (for Local Development)
            cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")
            if os.path.exists(cred_path):
                try:
                    logger.info(f"Attempting to initialize Firebase via file: {cred_path}")
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    logger.info("Successfully initialized Firebase via local file.")
                except Exception as e:
                    logger.error(f"Error initializing with local file: {e}")
                    firebase_admin.initialize_app()
            else:
                # Fallback to default credentials (works if GOOGLE_APPLICATION_CREDENTIALS is set)
                try:
                    logger.info("No explicit credentials found. Initializing via Default Credentials...")
                    firebase_admin.initialize_app()
                    logger.info("Successfully initialized Firebase via Default Credentials.")
                except Exception as e:
                    logger.error(f"Failed to initialize Firebase Default Credentials: {e}")
                    raise e # Re-raise if we have no other way to init
    
    return firestore.client()

try:
    db = init_firebase()
except Exception as e:
    logger.critical(f"FATAL ERROR: Could not initialize Firebase: {e}")
    # Don't let it crash silently; uvicorn will show this
    raise e
