from celery import Celery
from upscale import upscale

app = Celery(broker='redis://localhost:6379/1', backend='redis://localhost:6379/2')


@app.task()
def task_upscale(a, b):
    upscale(a, b)
