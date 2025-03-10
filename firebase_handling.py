import firebase_admin
from firebase_admin import credentials, firestore
from logger import logger
from config import CONFIG

def initialize_firebase() -> firestore.Client:
    try:
        cred = credentials.Certificate(CONFIG["firebase_key_path"])
        app = firebase_admin.initialize_app(cred)
        return firestore.client(app)
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise
