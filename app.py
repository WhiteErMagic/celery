import os
import uuid

from celery import Celery
from celery.result import AsyncResult
from flask import Flask, request, jsonify
from flask.views import MethodView

from upscale import upscale

from tasks import task_upscale


app_name = 'app'
app = Flask(app_name)
app.config['UPLOAD_FOLDER'] = 'files'
celery = Celery(app_name, broker='redis://localhost:6379/3', backend='redis://localhost:6379/4')
celery.conf.update(app.config)


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask


@celery.task()
def task_upscale():
    task1 = task_upscale()


class Photo(MethodView):

    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)
        return jsonify({'status': task.status, 'result': task.result})


    def get(self, file):
        return jsonify({'file': path})

    def post(self):
        image_path = self.save_image(field)
        task = task_upscale(image_path)
        return jsonify(
            {'task_id': task.id}
        )

    def save_image(self, field):
        image = request.files.get(field)
        extantion = image.filename.split('.')[-1]
        path = os.path('files', f'{uuid.uuid4()}.{extantion}')
        image.save(path)
        return path