import os
import csv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.inspection import inspect
from .models import Advertisement
from .init_db import SessionLocal

# Directory for CSV exports
EXPORT_DIR = "/app/dumps"

# Ensure the export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)


def export_to_csv():
    # Create a session
    session = SessionLocal()

    # Define the output CSV file
    output_file = os.path.join(EXPORT_DIR, "advertisements.csv")

    try:
        # Query all rows from the Advertisement table
        advertisements = session.query(Advertisement).all()

        # Dynamically get column names from the Advertisement model
        column_names = [column.key for column in inspect(Advertisement).columns]

        # Write rows to the CSV file
        with open(output_file, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            # Write the header row
            writer.writerow(column_names)
            # Write data rows
            for ad in advertisements:
                writer.writerow([getattr(ad, column) for column in column_names])

        print(f"Data exported successfully to {output_file}")
    except Exception as e:
        print(f"Failed to export data: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    export_to_csv()
