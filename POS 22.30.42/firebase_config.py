import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase app
def initialize_firebase():
    cred = credentials.Certificate("Enter your file path here")  # Update with your service account file path
    firebase_admin.initialize_app(cred)

# Get Firestore client
def get_firestore_client():
    return firestore.client()

# Initialize Firebase and get the Firestore client
initialize_firebase()
db = get_firestore_client()