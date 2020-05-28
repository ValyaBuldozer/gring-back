import os
from flask import request, abort, current_app
from uuid import uuid4


def upload_image(old_image):
    if 'image' not in request.files:
        return abort(400, 'No image to save')

    image = request.files['image']

    if image.filename == '':
        return abort(400, 'No image to save')

    ext = image.filename.rsplit('.', 1)[::-1][0].lower()

    if ext not in current_app.config['ALLOWED_IMAGE_EXTENSIONS']:
        return abort(400, 'This file type is not allowed')

    image.filename = str(uuid4()) + '.' + ext
    current_path = current_app.config['DIRNAME']
    assets_path = current_app.config['ASSETS_PATH']

    image.save(os.path.join(current_path, assets_path, image.filename))

    if old_image is not None:
        path = os.path.join(current_path, assets_path, old_image)
        if os.path.isfile(path):
            os.remove(os.path.join(current_path, assets_path, old_image))

    return image.filename


def delete_image(image):
    current_path = current_app.config['DIRNAME']
    assets_path = current_app.config['ASSETS_PATH']

    path = os.path.join(current_path, assets_path, image)
    if os.path.isfile(path):
        os.remove(os.path.join(current_path, assets_path, image))

    return True

