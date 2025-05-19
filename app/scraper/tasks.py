import os
import subprocess
from datetime import datetime
from celery import Celery
from celery.signals import worker_ready

from .models import Advertisement
from .init_db import SessionLocal
from .export_to_csv import export_to_csv
from .parse import get_all_advertisments

app = Celery("tasks", broker="redis://redis:6379")
app.config_from_object("app.scraper.celeryconfig")
LOG_FILE = "/app/dumps/datetime_log.txt"


def dump_db():
    db_name = os.getenv("POSTGRES_DB", "autos")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "secret")
    db_host = os.getenv("POSTGRES_HOST", "postgres")
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
def scrape_advertisements():
    session = SessionLocal()
    try:
        all_advert = session.query(Advertisement).all()
        links = [ad.url for ad in all_advert]
        print(f"Retrieved {len(links)} links from the database.")
    except Exception as e:
        print(f"Failed to retrieve links: {e}")
        links = []

    advertisements = get_all_advertisments(links)
    for advertisement in advertisements:
        try:
            session.add(advertisement)
            session.commit()
            print(f"Saved advertisement: {advertisement.url}")
        except Exception as e:
            session.rollback()
            print(f"Failed to save advertisement: {e}")
        finally:
            session.close()
    dump_db()
    export_to_csv()


@worker_ready.connect
def at_startup(sender, **kwargs):
    print("Running scrape_advertisements task at startup...")
    scrape_advertisements.delay()
