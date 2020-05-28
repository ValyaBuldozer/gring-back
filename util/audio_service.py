import os
from flask import request, abort, current_app
from uuid import uuid4


def upload_audio(old_audio):
    if 'audio' not in request.files:
        return abort(400, 'No audio to save')

    audio = request.files['audio']

    if audio.filename == '':
        return abort(400, 'No audio to save')

    ext = audio.filename.rsplit('.', 1)[::-1][0].lower()

    if ext not in current_app.config['ALLOWED_AUDIO_EXTENSIONS']:
        return abort(400, 'This file type is not allowed')

    audio.filename = str(uuid4()) + '.' + ext
    current_path = current_app.config['DIRNAME']
    assets_path = current_app.config['ASSETS_PATH']

    audio.save(os.path.join(current_path, assets_path, audio.filename))

    if old_audio is not None:
        path = os.path.join(current_path, assets_path, old_audio)
        if os.path.isfile(path):
            os.remove(os.path.join(current_path, assets_path, old_audio))

    return audio.filename


def delete_audio(audio):
    current_path = current_app.config['DIRNAME']
    assets_path = current_app.config['ASSETS_PATH']

    path = os.path.join(current_path, assets_path, audio)
    if os.path.isfile(path):
        os.remove(os.path.join(current_path, assets_path, audio))

    return True
