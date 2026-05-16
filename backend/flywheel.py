import re
import json
import chromadb
from chromadb.config import Settings
import os

# Initialize Vector DB
CHROMA_PATH = "data/vector_db"
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="hynix_memory")

def sanitize_teacher_response(response: str) -> bool:
    """
    Sanitizes the teacher's response based on Pillar 2 requirements.
    Must contain <think> tags and valid JSON if tool calling is implied.
    """
    # 1. Check for <think> tags
    if "<think>" not in response or "</think>" not in response:
        return False
    
    # 2. Check for tool call consistency
    if "<json>" in response:
        if "</json>" not in response:
            return False
        
        # Validate JSON content
        try:
            json_str = re.search(r'<json>(.*?)</json>', response, re.DOTALL).group(1)
            json.loads(json_str)
        except (AttributeError, json.JSONDecodeError):
            return False
            
    return True

def add_to_long_term_memory(prompt: str, response: str):
    """Stores high-quality interaction into ChromaDB for RAG."""
    collection.add(
        documents=[f"User: {prompt}\nAI: {response}"],
        metadatas=[{"source": "teacher_flywheel"}],
        ids=[f"msg_{os.urandom(4).hex()}"]
    )

def query_memory(query: str, n_results: int = 3):
    """Retrieves relevant context from vector memory."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results['documents'][0] if results['documents'] else []
