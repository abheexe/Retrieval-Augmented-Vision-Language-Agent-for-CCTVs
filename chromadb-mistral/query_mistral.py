import chromadb
from chromadb.utils import embedding_functions

# 1. Connect to the SAME database folder
client = chromadb.PersistentClient(path="./security_memory")
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_collection(name="vlm_logs", embedding_function=emb_fn)

def fetch_and_answer(user_question):
    # SEARCH: Find the 2 most relevant logs
    results = collection.query(
        query_texts=[user_question],
        n_results=2
    )
    
    # EXTRACT: Get the text of the logs found
    retrieved_context = "\n".join(results['documents'][0])
    
    if not retrieved_context:
        return "No matching logs found in the database."

    # PROMPT: This is what you send to Mistral
    final_prompt = f"""
    You are a Security Assistant. Use the logs below to answer the question.
    If the answer isn't in the logs, say 'Data not found'.
    
    LOGS:
    {retrieved_context}
    
    USER QUESTION: {user_question}
    """
    
    print("--- EVIDENCE FOUND ---")
    print(retrieved_context)
    print("\n--- PROMPT FOR MISTRAL ---")
    print(final_prompt)
    
    # Note: You would call mistral_client.chat() here with final_prompt
    return "Ready to send to Mistral!"

# --- TEST THE SEARCH ---
if __name__ == "__main__":
    print(fetch_and_answer("Who was wearing a red hoodie?"))