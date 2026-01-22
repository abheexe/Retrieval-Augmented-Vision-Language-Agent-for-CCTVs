import chromadb
from chromadb.utils import embedding_functions
import json
import time

# --- STEP A: INITIALIZATION ---
# Persistent storage ensures data stays on your disk
client = chromadb.PersistentClient(path="./security_simulation_db")
# Using the standard embedding model for semantic search
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(name="simulated_logs", embedding_function=emb_fn)

# --- STEP B: PREPARING THE "STREAM" ---
# This list simulates your VLM sending data over several minutes
vlm_stream_simulation = [
    {
        "camera_id": "Main_Entrance",
        "timestamp": "2026-01-23 09:00:00",
        "persons": [
            {"description": "A man in a blue suit holding a black briefcase", "activity": "scanning an ID card at the turnstile"},
            {"description": "A security guard in a grey uniform", "activity": "nodding at the visitor"}
        ]
    },
    {
        "camera_id": "Loading_Dock",
        "timestamp": "2026-01-23 09:15:00",
        "persons": [
            {"description": "A worker in a high-visibility orange vest", "activity": "operating a manual pallet jack with a heavy crate"}
        ]
    },
    {
        "camera_id": "Staff_Cafeteria",
        "timestamp": "2026-01-23 12:30:00",
        "persons": [
            {"description": "A group of three employees", "activity": "sitting at a round table and talking"},
            {"description": "A woman in a white lab coat", "activity": "carrying a tray with a coffee cup and a sandwich"}
        ]
    },
    {
        "camera_id": "Parking_Lot_B",
        "timestamp": "2026-01-23 13:45:00",
        "persons": [
            {"description": "A person wearing a dark hoodie and a backpack", "activity": "lingering near a locked bicycle rack while looking around nervously"}
        ]
    },
    {
        "camera_id": "Server_Room",
        "timestamp": "2026-01-23 14:10:00",
        "persons": [
            {"description": "A technician wearing a blue polo shirt", "activity": "holding a laptop and connecting a cable to a server rack"}
        ]
    },
    {
        "camera_id": "Lobby",
        "timestamp": "2026-01-23 15:05:00",
        "persons": [
            {"description": "A courier in a red polo shirt", "activity": "holding a cardboard package and waiting at the reception desk"}
        ]
    },
    {
        "camera_id": "Exit_Gate_04",
        "timestamp": "2026-01-23 17:00:00",
        "persons": [
            {"description": "Multiple people (approximately 5)", "activity": "exiting the building in a group as the workday ends"}
        ]
    },
    {
        "camera_id": "Warehouse_Aisle_4",
        "timestamp": "2026-01-23 18:20:00",
        "persons": [
            {"description": "A man in denim overalls", "activity": "climbing a ladder while holding a flashlight"}
        ]
    },
    {
        "camera_id": "Front_Desk",
        "timestamp": "2026-01-23 20:00:00",
        "persons": [
            {"description": "A janitor in a green jumpsuit", "activity": "pushing a large cleaning cart with various bottles and tools"}
        ]
    },
    {
        "camera_id": "Rear_Alleyway",
        "timestamp": "2026-01-23 23:55:00",
        "persons": [
            {"description": "Two individuals in dark clothing", "activity": "standing near the dumpster and holding a suspicious duffel bag"}
        ]
    }
]

# --- STEP C: THE INGESTION ENGINE ---
def simulate_ingestion(stream):
    print("--- STARTING DATA INGESTION SIMULATION ---")
    for frame in stream:
        ts = frame['timestamp']
        cam = frame['camera_id']
        
        for i, person in enumerate(frame['persons']):
            # 1. Flatten into text
            doc_text = f"At {ts} on {cam}, {person['description']} was observed {person['activity']}."
            
            # 2. Assign unique ID and metadata
            doc_id = f"{cam}_{ts}_{i}"
            metadata = {"time": ts, "camera": cam}
            
            # 3. Store in Vector DB
            collection.add(documents=[doc_text], metadatas=[metadata], ids=[doc_id])
            print(f"✅ Stored Log: {doc_id}")
            time.sleep(0.1) # Faster simulation delay
    print("--- INGESTION COMPLETE ---\n")

# --- STEP D: THE MISTRAL QUERY INTERFACE ---
def get_mistral_response(query):
    # 1. Retrieve the Top 2 matching logs
    results = collection.query(query_texts=[query], n_results=2)
    
    # 2. Extract and format context
    evidence = "\n".join(results['documents'][0])
    
    # 3. Construct the Mistral-ready prompt
    prompt = f"""
    SYSTEM: You are a Surveillance AI. Answer the question using ONLY the logs provided.
    
    LOGS:
    {evidence}
    
    USER QUESTION: {query}
    AI RESPONSE:
    """
    return prompt

# --- RUNNING THE INTERACTIVE SIMULATION ---

# Part 1: First, we populate the database with our 10 scenarios
simulate_ingestion(vlm_stream_simulation)

# Part 2: Interactive loop
print("--- SURVEILLANCE INTERFACE READY ---")
print("Enter your queries below. Type 'exit' to quit.")

while True:
    # Wait for your real-time input
    user_input = input("\nQuery: ")
    
    # Exit check
    if user_input.lower() == "exit":
        print("Exiting simulation...")
        break
    
    # Process the query and get the prompt
    final_output = get_mistral_response(user_input)
    
    print("\n--- FINAL PROMPT FOR MISTRAL ---")
    print(final_output)