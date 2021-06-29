import os

app_config = {
    "host": os.getenv("host", "0.0.0.0"),
    "port": os.getenv("port", 8000)
}

celery_config = {
    "backend": os.getenv("celery_backend", "redis://:password123@redis:6379/0"),
    "broker": os.getenv("celery_broker", "redis://:password123@redis:6379/0")
}
