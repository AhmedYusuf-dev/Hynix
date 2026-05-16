import sqlite3
import json
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from backend.database.security import decrypt_data # Internal DB decryption

# Project Identity: Hynix 1 Mini
# Pillar 5: Ghost Pipeline - Alignment with Flywheel DB

load_dotenv()

# Internal DB Path (matching db.py)
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/logs/flywheel.db"))

def get_master_key():
    key = os.getenv("HYNIX_MASTER_KEY")
    if not key:
        key = Fernet.generate_key().decode()
        print(f"CRITICAL: New Master Key Generated: {key}")
        print("SAVE THIS TO YOUR .env AS HYNIX_MASTER_KEY")
    return key.encode()

def export_encrypted_dataset(output_path="data/ghost_dataset.enc"):
    if not os.path.exists("data"): os.makedirs("data")
    if not os.path.exists(DB_PATH):
        print(f"Error: Hynix Vault not found at {DB_PATH}. Run the backend first to generate logs.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Pillar 5: Fetching from 'logs' table
    cursor.execute("SELECT prompt, response, agent_metadata FROM logs")
    rows = cursor.fetchall()
    
    dataset = []
    for enc_prompt, enc_response, metadata_json in rows:
        metadata = json.loads(metadata_json) if metadata_json else {}
        
        # Only export sanitized interactions for quality
        if metadata.get("type") in ["sanitized_flywheel", "agentic_flywheel"]:
            # Decrypt from local database security first
            prompt = decrypt_data(enc_prompt)
            response = decrypt_data(enc_response)
            
            dataset.append({
                "instruction": prompt,
                "output": response
            })
    
    if not dataset:
        print("Warning: No sanitized interactions found in Flywheel DB. Start chatting to build the dataset!")
        return

    # Ghost Pipeline Encryption
    raw_data = json.dumps(dataset).encode()
    f = Fernet(get_master_key())
    encrypted_data = f.encrypt(raw_data)
    
    with open(output_path, "wb") as f_out:
        f_out.write(encrypted_data)
    
    print(f"Hynix 1 Mini: Ghost Dataset exported ({len(dataset)} samples) to {output_path}")
    conn.close()

if __name__ == "__main__":
    export_encrypted_dataset()
