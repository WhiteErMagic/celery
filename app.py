import os
import uuid

from celery import Celery
from celery.result import AsyncResult
from flask import Flask, request, jsonify
from flask.views import MethodView

from upscale import upscale

from tasks import task_upscale
from flask import send_file


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
def task_upscale(image_path, output_path):
    upscale(image_path, output_path)
    return output_path


@app.route('/processed/<string:name>')
def download_file(name):
    return send_file(name)


class Photo(MethodView):

    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)
        return jsonify({'status': task.status, 'result': task.result})

    def post(self):
        image_path_in = ('image_1')
        image_path = self.save_image(image_path_in)
        output_path = self.upscale_path(image_path_in)
        task_upscale(image_path, output_path)
        return jsonify(
            {'output_path': output_path}
        )

    def upscale_path(self, field):
        image = request.files.get(field)
        extantion = image.filename.split('.')[-1]
        path = os.path.join('files', f'{uuid.uuid4()}.{extantion}')
        return path

    def save_image(self, field):
        image = request.files.get(field)
        extantion = image.filename.split('.')[-1]
        path = os.path.join('files', f'{uuid.uuid4()}.{extantion}')
        image.save(path)
        return path


photo_view = Photo.as_view('photo')
app.add_url_rule('/processed/<string:name>', view_func=download_file, methods=['GET'])
app.add_url_rule('/photo/<string:id>', view_func=photo_view, methods=['GET'])
app.add_url_rule('/upscale/', view_func=photo_view, methods=['POST'])


if __name__ == '__main__':
    app.run()