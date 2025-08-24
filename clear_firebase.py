import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Configuration
FIREBASE_PROJECT_ID = "cooksat-sat-questions"
FIREBASE_SERVICE_ACCOUNT_KEY_PATH = "./cooksat-sat-questions-firebase-adminsdk-fbsvc-25a836b83a.json"

def delete_collection_recursive(db, collection_ref, batch_size=10):
    """Recursively delete a collection and all its subcollections"""
    docs = collection_ref.limit(batch_size).stream()
    deleted = 0
    
    for doc in docs:
        print(f"   Deleting document: {doc.id}")
        # Delete all subcollections first
        subcollections = doc.reference.collections()
        for subcollection in subcollections:
            print(f"     Deleting subcollection: {subcollection.id}")
            delete_collection_recursive(db, subcollection, batch_size)
        
        # Delete the document
        doc.reference.delete()
        deleted += 1
    
    # If there are more documents, delete them in batches
    if deleted >= batch_size:
        return delete_collection_recursive(db, collection_ref, batch_size)
    
    return deleted

def clear_firebase_data():
    """Clear all existing data from Firebase"""
    try:
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
            firebase_admin.initialize_app(cred, {
                'projectId': FIREBASE_PROJECT_ID
            })
            print("✅ Firebase initialized successfully")
        
        # Get Firestore client
        db = firestore.client()
        print("✅ Firestore client ready")
        
        # Clear the questions collection and all its subcollections
        print("🗑️ Clearing questions collection and all subcollections...")
        questions_ref = db.collection('questions')
        
        # Recursively delete everything
        deleted_count = delete_collection_recursive(db, questions_ref)
        
        print(f"✅ Successfully deleted {deleted_count} documents and all subcollections")
        print("🧹 Firebase is now completely clean and ready for the new subcollection structure!")
        
    except Exception as e:
        print(f"❌ Error clearing Firebase: {e}")

if __name__ == "__main__":
    clear_firebase_data()
