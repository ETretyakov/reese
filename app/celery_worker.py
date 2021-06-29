from celery_app import celery_app
from celery import current_task

from tools.analyzers import Document
from binascii import a2b_base64


class Task:
    def __init__(self, file: bytes, language: str):
        self.file = file
        self.language = language

    def execute(self):
        data = {}

        document = Document(file=self.file, language=self.language)
        current_task.update_state(state='PROGRESS', meta={'process_percent': 30})

        data["wcag_compliance"] = document.wcag_compliance()
        current_task.update_state(state='PROGRESS', meta={'process_percent': 50})

        data["volume_compliance"] = document.volume()
        current_task.update_state(state='PROGRESS', meta={'process_percent': 60})

        data["text_size_compliance"] = ...
        current_task.update_state(state='PROGRESS', meta={'process_percent': 70})

        data["font_compliance"] = ...
        current_task.update_state(state='PROGRESS', meta={'process_percent': 90})

        return data


@celery_app.task(name="evaluate_presentation", acks_late=True)
def execute_query(file: str, language: str) -> dict:

    file = a2b_base64(file.encode("utf-8"))

    task = Task(file=file, language=language)
    wcag_compliance = task.execute()

    return {
        "wcag_compliance": wcag_compliance
    }
