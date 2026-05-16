import sqlite3
import json
import os
import re
from backend.database.security import decrypt_data

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/logs/flywheel.db")
EXPORT_PATH = os.path.join(os.path.dirname(__file__), "../data/exports/hynix_secure_batch.jsonl")

def strip_pii(text: str) -> str:
    """Basic PII scrubber for emails and phone numbers."""
    # Scrub Emails
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL_REDACTED]', text)
    # Scrub Phone Numbers (US/International rough match)
    text = re.sub(r'\+?\d[\d -]{8,12}\d', '[PHONE_REDACTED]', text)
    return text

def export_secure_to_jsonl():
    if not os.path.exists(DB_PATH):
        print("No database found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT prompt, response FROM logs")
    rows = cursor.fetchall()
    
    with open(EXPORT_PATH, "w", encoding="utf-8") as f:
        count = 0
        for enc_prompt, enc_response in rows:
            try:
                # Decrypt
                prompt = decrypt_data(enc_prompt)
                response = decrypt_data(enc_response)
                
                # Pillar 3: PII Sanitization
                clean_prompt = strip_pii(prompt)
                clean_response = strip_pii(response)
                
                entry = {
                    "instruction": clean_prompt,
                    "input": "",
                    "output": clean_response
                }
                f.write(json.dumps(entry) + "\n")
                count += 1
            except Exception as e:
                print(f"Skipping row due to decryption error: {e}")
            
    conn.close()
    print(f"Securely exported {count} samples to {EXPORT_PATH}")

if __name__ == "__main__":
    export_secure_to_jsonl()
