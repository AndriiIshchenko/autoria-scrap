from celery.schedules import crontab

# Celery configuration
broker_url = "redis://redis:6379"
result_backend = "redis://redis:6379"

# Celery Beat schedule
beat_schedule = {
    "log-datetime-every-20-seconds": {
        "task": "app.scraper.tasks.log_datetime",
        "schedule": 20.0,  # Run every 20 seconds
    },
    "create_adv-20-seconds": {
        "task": "app.scraper.tasks.cretate_avd",
        "schedule": 15.0,  # Run every 20 seconds
    },
    "dump-32-seconds": {
        "task": "app.scraper.tasks.dump_db",
        "schedule": 32.0,  # Run every 20 seconds
    },
    "csv-25-seconds": {
        "task": "app.scraper.tasks.export_to_csv_task",
        "schedule": 32.0,  # Run every 20 seconds
    },
}

timezone = "UTC"
