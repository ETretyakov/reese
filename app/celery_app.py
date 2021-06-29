from celery import Celery

from config import celery_config

celery_app = Celery(
    "worker",
    backend=celery_config["backend"],
    broker=celery_config["broker"]
)

celery_app.conf.task_routes = {
    "celery_worker.evaluate_presentation": "evaluate-presentation"
}

celery_app.conf.update(task_track_started=True)
