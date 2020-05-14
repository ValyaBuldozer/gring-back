import os
from flask import request, abort, current_app
from uuid import uuid4


def upload_image(image_field):
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

    if image_field is not None:
        path = os.path.join(current_path, assets_path, image_field)
        if os.path.isfile(path):
            os.remove(os.path.join(current_path, assets_path, image_field))

    return image.filename
