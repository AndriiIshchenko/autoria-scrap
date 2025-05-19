from math import e
import os
import subprocess
import random
from datetime import datetime
from celery import Celery
from celery.signals import worker_ready
from sqlalchemy.orm import sessionmaker
from .models import Advertisement
from .init_db import SessionLocal

from .export_to_csv import export_to_csv
from .parse import get_all_advertisments

app = Celery("tasks", broker="redis://redis:6379")
# Add this line to load the configuration
app.config_from_object("app.scraper.celeryconfig")
LOG_FILE = "/app/dumps/datetime_log.txt"


@app.task
def scrape_advertisements():
    session = SessionLocal()
    try:
        all_advert = session.query(Advertisement).all()
        links = [ad.url for ad in all_advert]
        print(f"Retrieved {len(links)} links from the database.")

    except Exception as e:
        print(f"Failed to retrieve links: {e}")
        links =  []
    
    advertisements = get_all_advertisments(links)
    for advertisement in advertisements:
        try:
            # Add the advertisement to the session
            session.add(advertisement)
            session.commit()
            print(f"Saved advertisement: {advertisement.url}")
        except Exception as e:
            session.rollback()
            print(f"Failed to save advertisement: {e}")
        finally:
            session.close()

@app.task
def export_to_csv_task():
    export_to_csv()

@app.task
def dump_db():
    db_name = os.getenv("POSTGRES_DB", "autos")  # Use environment variables
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv(
        "POSTGRES_PASSWORD", "secret"
    )  # Get the password from the environment
    db_host = os.getenv(
        "POSTGRES_HOST", "postgres"
    )  # Hostname of the PostgreSQL service
    output_dir = "/app/dumps"
    output_file = f"{output_dir}/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dump"

    os.makedirs(output_dir, exist_ok=True)

    command = [
        "pg_dump",
        "-U",
        db_user,
        "-h",
        db_host,
        "-F",
        "c",
        "-d",
        db_name,
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    try:
        with open(output_file, "wb") as f:
            subprocess.run(command, stdout=f, check=True, env=env)
        print(f"Database dumped successfully to {output_file}")
    except subprocess.CalledProcessError as e:
        print("Error during pg_dump:", e)

@app.task
def log_datetime():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(LOG_FILE, "a") as file:
            file.write(current_time + "\n")
        print(f"Logged datetime: {current_time}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

# @app.task
# def cretate_avd():
#     advertisements = [
#         Advertisement(
#             url=f"https://auto.ria.com/car/used/page-{i}{random.randint(1000, 9999)}/"
#         )
#         for i in range(1, 10)
#     ]
#     try:
#         session.add_all(advertisements)
#         session.commit()
#         print(f"Saved {len(advertisements)} advertisements to the database.")
#     except Exception as e:
#         session.rollback()
#         print(f"Failed to save advertisements: {e}")

@worker_ready.connect
def at_startup(sender, **kwargs):
    print("Running scrape_advertisements task at startup...")
    scrape_advertisements.delay()
