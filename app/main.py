from fastapi import FastAPI, File, BackgroundTasks
from fastapi.responses import JSONResponse

from celery.result import AsyncResult
from celery_app import celery_app

from binascii import b2a_base64

import logging

log = logging.getLogger(__name__)

app = FastAPI()


def celery_on_message(body):
    log.warning(body)


def background_on_message(task):
    log.warning(task.get(on_message=celery_on_message, propagate=False))


@app.get("/")
def read_root():
    return {
        "name": "reese",
        "type": "service",
        "description": "REESE (pResentation ExpErt SErvice) - "
                       "the software aimed at evaluation of presentation documents in PDF format.",
        "documentation": "/docs",
        "version": "0.0.1"
    }


@app.post("/tasks/create/")
async def create_task(background_task: BackgroundTasks, file: bytes = File(...), language: str = "eng"):
    task_name = "evaluate_presentation"

    try:
        file_string = b2a_base64(file).decode("utf-8")
        task = celery_app.send_task(task_name, args=(file_string, language))
        background_task.add_task(background_on_message, task)
        status, message = True, f"Created: [TaskID] {task.id}"
    except Exception as error:
        status, message = False, f"[Creating task] {type(error).__name__}: {str(error)}"

    return JSONResponse({"status": status, "message": message})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)

    result = {
        "task_id": task_id,
        "task_status": str(task_result.status),
        "task_result": str(task_result.result)
    }

    return JSONResponse(result)
