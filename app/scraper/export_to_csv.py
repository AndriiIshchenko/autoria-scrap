import os
import csv

from sqlalchemy.inspection import inspect

from .models import Advertisement
from .init_db import SessionLocal

EXPORT_DIR = "/app/dumps"
os.makedirs(EXPORT_DIR, exist_ok=True)


def export_to_csv():
    session = SessionLocal()
    output_file = os.path.join(EXPORT_DIR, "advertisements.csv")

    try:
        advertisements = session.query(Advertisement).all()
        column_names = [column.key for column in inspect(Advertisement).columns]

        with open(output_file, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_names)
            for ad in advertisements:
                writer.writerow([getattr(ad, column) for column in column_names])

        print(f"Data exported successfully to {output_file}")
    except Exception as e:
        print(f"Failed to export data: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    export_to_csv()
