import os


TIMEZONE = "Europe/Moscow"

BROKER_URL = os.environ.get("CELERY_BROKER_URL")
RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
