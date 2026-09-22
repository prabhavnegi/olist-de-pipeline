from sqlalchemy import create_engine, text
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

def get_engine():
    load_dotenv()
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    db_host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    db_port = os.getenv("POSTGRES_PORT", 5432)
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(db_url)

def create_schema(engine, schema_name):
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name};"))