from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load secret environment variables from the .env file (like the Supabase URL)
load_dotenv()

# Get the Supabase database connection string
DATABASE_URL = os.getenv("DATABASE_URL")

fallback_sqlite = "sqlite:///./local_dashboard.db"
engine = None

if DATABASE_URL:
    try:
        # Create engine for PostgreSQL with a short connection timeout
        if "postgresql" in DATABASE_URL:
            # Append connect_timeout=3 to the connection string
            separator = "&" if "?" in DATABASE_URL else "?"
            test_url = f"{DATABASE_URL}{separator}connect_timeout=3"
        else:
            test_url = DATABASE_URL
        
        # Test connection
        temp_engine = create_engine(test_url)
        with temp_engine.connect() as conn:
            pass
        engine = temp_engine
        print("Successfully connected to the remote database!")
    except Exception as e:
        print(f"\n[WARNING] Could not connect to remote database: {e}")
        print("Falling back to local SQLite database: local_dashboard.db\n")
        engine = create_engine(fallback_sqlite, connect_args={"check_same_thread": False})
else:
    print("\nDATABASE_URL not found. Using local SQLite database: local_dashboard.db\n")
    engine = create_engine(fallback_sqlite, connect_args={"check_same_thread": False})

# Create a factory that generates new database sessions for our requests
SessionLocal = sessionmaker(
    autocommit=False, # We want to manually commit our changes to be safe
    autoflush=False,
    bind=engine
)

# Base class for our database models. We use this to define our tables in Python.
Base = declarative_base()

# A helpful function that gives us a database session when we need one
# and safely closes it when we are done. We use this in our API routes.
def get_db():
    db = SessionLocal()
    try:
        yield db # Give the session to the part of the app asking for it
    finally:
        db.close() # Always close the session when finished!