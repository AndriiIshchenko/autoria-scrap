import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from .models import Base

# Get the database URL from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# Retry logic to wait for the database to be ready
MAX_RETRIES = 10
WAIT_SECONDS = 5

for attempt in range(MAX_RETRIES):
    try:
        # Create the SQLAlchemy engine
        engine = create_engine(DATABASE_URL)
        # Test the connection
        with engine.connect() as connection:
            print("Database is ready!")
        break
    except OperationalError:
        print(f"Database is not ready yet. Retrying in {WAIT_SECONDS} seconds...")
        time.sleep(WAIT_SECONDS)
else:
    raise Exception("Failed to connect to the database after multiple retries.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
