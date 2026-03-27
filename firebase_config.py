import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

def init_firebase():
    """Initializes the Firebase Admin SDK."""
    # Use environment variable or default filename
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")
    
    if not firebase_admin._apps:
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback for CI/Environment variables if needed
            print(f"Warning: {cred_path} not found. Using default application credentials.")
            firebase_admin.initialize_app()
    
    return firestore.client()

db = init_firebase()
