import os
from celery.schedules import crontab

# Celery configuration
broker_url = "redis://redis:6379"
result_backend = "redis://redis:6379"

# Celery Beat schedule
beat_schedule = {
    # "scrape_advertisements": {
    #     "task": "app.scraper.tasks.scrape_advertisements",
    #     "schedule": 600
    # },
    # "create_adv-20-seconds": {
    #     "task": "app.scraper.tasks.cretate_avd",
    #     "schedule": 350.0,  # Run every 20 seconds
    # },
    # "dump-32-seconds": {
    #     "task": "app.scraper.tasks.dump_db",
    #     "schedule": 350.0,  # Run every 20 seconds
    # },
    "csv-25-seconds": {
        "task": "app.scraper.tasks.export_to_csv_task",
        "schedule": 600.0,  # Run every 20 seconds
    },
}

timezone = "UTC"
