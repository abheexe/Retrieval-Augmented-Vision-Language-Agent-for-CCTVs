import chromadb
from chromadb.utils import embedding_functions
import json

# 1. Initialize the Database (Saves to 'security_memory' folder)
client = chromadb.PersistentClient(path="./security_memory")

# 2. Define the Brain (The model that turns text into vectors)
# This model is small, fast, and great for security logs
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 3. Create a 'Collection' (Like a table in a database)
collection = client.get_or_create_collection(name="vlm_logs", embedding_function=emb_fn)

def save_json_to_db(vlm_json):
    """Converts VLM JSON into searchable vector chunks."""
    timestamp = vlm_json.get("timestamp", "unknown_time")
    cam_id = vlm_json.get("camera_id", "cam_01")
    
    # We store each person as a separate 'document' so search is precise
    for i, person in enumerate(vlm_json['persons']):
        # FLATTENING: Turn JSON fields into a sentence the AI can 'understand'
        searchable_text = f"At {timestamp}, {person['description']} was spotted {person['activity']}."
        
        # METADATA: Keep the raw data for filtering (not for searching)
        metadata = {"time": timestamp, "camera": cam_id, "person_index": i}
        
        # SAVE: Push to ChromaDB
        collection.add(
            documents=[searchable_text],
            metadatas=[metadata],
            ids=[f"{cam_id}_{timestamp}_{i}"]
        )
    print(f"Successfully stored {len(vlm_json['persons'])} logs in ChromaDB.")

# --- QUICK TEST: Run this to see if it saves properly ---
if __name__ == "__main__":
    sample_data = {
        "camera_id": "Entry_Gate",
        "timestamp": "2025-10-04 18:45:15",
        "persons": [
            {"description": "Woman in a black shirt and glasses", "activity": "entering the building"},
            {"description": "Man in a red hoodie", "activity": "running away"}
        ]
    }
    save_json_to_db(sample_data)