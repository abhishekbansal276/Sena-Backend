import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import json

def init_firebase():
    """Initializes the Firebase Admin SDK from file OR environment variable."""
    if not firebase_admin._apps:
        # 1. OPTION A: Check if the JSON is in an Environment Variable (for Render)
        env_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        
        if env_json:
            try:
                # Parse the JSON string from the environment variable
                cred_dict = json.loads(env_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                print("Firebase initialized via Environment Variable.")
            except Exception as e:
                print(f"Error parsing FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
                firebase_admin.initialize_app()
        else:
            # 2. OPTION B: Look for the local file (for Local Development)
            cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print(f"Firebase initialized via file: {cred_path}")
            else:
                # Fallback to default credentials (can be set via GOOGLE_APPLICATION_CREDENTIALS)
                try:
                    firebase_admin.initialize_app()
                    print("Firebase initialized via Default Credentials.")
                except Exception as e:
                    print(f"Failed to initialize Firebase: {e}")
    
    return firestore.client()

db = init_firebase()
