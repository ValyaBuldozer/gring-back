from yandex_translate import YandexTranslate
from flask import current_app


def translation_init():
    global translate
    translate = YandexTranslate(current_app.config['YANDEX_KEY'])
