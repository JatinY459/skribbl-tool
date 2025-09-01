import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin") # Default to 'admin' if not set

# --- MONGODB CLIENT SETUP ---
# Create a single, reusable client instance
try:
    client = MongoClient(DATABASE_URL)
    # The ismaster command is cheap and does not require auth. It's a quick way to test the connection.
    client.admin.command('ismaster') 
    db = client.skribblDB # Your database name
    word_collections = db.word_collections # The collection (like a SQL table) that holds all our data
except (ConnectionFailure, AttributeError) as e:
    print(f"Error: Could not connect to MongoDB. Please check your DATABASE_URL. {e}")
    client = None # Set client to None if connection fails

# In MongoDB, you don't need to initialize tables. The database and collections
# are created automatically the first time you insert data into them.
# So, the init_db() function is no longer needed.

def create_collection(collection_name: str):
    """Creates a new, empty collection document."""
    collection_name = collection_name.strip().lower()
    if not client or not collection_name: return False

    # Check if a document with this name (_id) already exists
    if word_collections.find_one({"_id": collection_name}):
        return False # Collection already exists
    else:
        # Insert a new document with the name as the ID and an empty words array
        word_collections.insert_one({"_id": collection_name, "words": []})
        return True

def get_all_collections():
    """Fetches a list of all collection names."""
    if not client: return []
    # Find all documents, but only return their _id field.
    collections_cursor = word_collections.find({}, {"_id": 1}).sort("_id", 1)
    return [doc["_id"] for doc in collections_cursor]

def get_word_count(collection_name: str):
    """Efficiently counts the number of words in a collection."""
    if not client: return 0
    doc = word_collections.find_one({"_id": collection_name})
    return len(doc.get("words", [])) if doc else 0

def add_word(collection_name: str, word: str):
    """Adds a word to a specific collection's words array, preventing duplicates."""
    word = word.strip().lower()
    if not client or not word: return "Error: Word cannot be empty."

    # Use the $addToSet operator to add the word only if it's not already present.
    # This is an atomic and efficient way to prevent duplicates.
    result = word_collections.update_one(
        {"_id": collection_name},
        {"$addToSet": {"words": word}}
    )

    if result.modified_count > 0:
        return f"Success! Added '{word.capitalize()}'."
    else:
        # If nothing was modified, it means the word was already in the set.
        return f"'{word.capitalize()}' is already in this collection."

def delete_collection(collection_name: str):
    """Deletes an entire collection document."""
    if not client: return "Error: Could not connect to the database."
    word_collections.delete_one({"_id": collection_name})
    return f"Success! Collection '{collection_name}' has been deleted."

def view_words(collection_name: str, password: str):
    """Returns a comma-separated string of words if the password is correct."""
    if password != ADMIN_PASSWORD:
        return "Error: Incorrect password."
    if not client: return "Error: Could not connect to the database."
        
    doc = word_collections.find_one({"_id": collection_name})
    
    if not doc:
        return f"Collection '{collection_name}' does not exist."

    words = sorted(doc.get("words", []), key=str.lower)
    
    return ", ".join(words) if words else f"The '{collection_name}' collection is empty."