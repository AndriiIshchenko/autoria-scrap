from celery.schedules import crontab


broker_url = "redis://redis:6379"
result_backend = "redis://redis:6379"

beat_schedule = {
    "scrape_advertisements": {
        "task": "app.scraper.tasks.scrape_advertisements",
        "schedule": crontab(hour=9, minute=0),
    },
}

timezone = "UTC"
