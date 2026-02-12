import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth

load_dotenv()

# Initialize Firebase Admin SDK
cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')

try:
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("✓ Firebase initialized")
    else:
        print(f"⚠ Firebase credentials not found at {cred_path}")
        print("  Authentication will be disabled until credentials are added")
except Exception as e:
    print(f"⚠ Firebase initialization failed: {e}")

def verify_token(id_token):
    """Verify Firebase ID token and return user info"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {
            "uid": decoded_token['uid'],
            "email": decoded_token.get('email'),
            "success": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
