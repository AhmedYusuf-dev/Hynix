import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.database.security import encrypt_data, decrypt_data
from dotenv import load_dotenv

# Project Identity: Hynix 1 Mini
# Global Flywheel: Hybrid Database Logic (SQLite + PostgreSQL)

load_dotenv()

# Use DATABASE_URL from environment (Supabase) or fallback to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/logs/flywheel.db")

# Fix for Render/Heroku postgres:// vs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class InteractionLog(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    prompt = Column(Text)
    response = Column(Text)
    model_name = Column(String(100))
    agent_metadata = Column(Text)

def init_db():
    if not os.path.exists("./data/logs") and "sqlite" in DATABASE_URL:
        os.makedirs("./data/logs")
    Base.metadata.create_all(bind=engine)
    print(f"Hynix 1 Mini: Flywheel DB Initialized ({'Cloud' if 'postgres' in DATABASE_URL else 'Local'})")

def log_interaction(prompt, response, model_name, agent_metadata=None):
    db = SessionLocal()
    try:
        # Pillar 2: Encrypted Data Logging
        enc_prompt = encrypt_data(prompt)
        enc_response = encrypt_data(response)
        
        new_log = InteractionLog(
            prompt=enc_prompt,
            response=enc_response,
            model_name=model_name,
            agent_metadata=json.dumps(agent_metadata)
        )
        db.add(new_log)
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
