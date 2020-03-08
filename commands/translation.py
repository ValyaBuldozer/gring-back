from flask import Blueprint, current_app
from models.Language import Language
from models.base import get_session
from models.LocaleString import LocaleString
import click
from yandex_translate import YandexTranslate

translation_command_blueprint = Blueprint('translation', __name__)


@translation_command_blueprint.cli.command("create-locale")
@click.argument("locale")
@click.argument('with_update')
def create_locale(locale, with_update):
    if locale is None or locale not in Language.__members__:
        print('%s is unsupported language' % locale)
        return

    if with_update is None:
        with_update = False

    translate = YandexTranslate(current_app.config['YANDEX_KEY'])
    session = get_session()

    ru_strings = session.query(LocaleString).filter(
        LocaleString.locale == Language.ru
    ).all()

    for string in ru_strings:
        target_string = session.query(LocaleString).filter(
            LocaleString.id == string.id,
            LocaleString.locale == locale
        ).first()

        if target_string is None:
            translation = translate.translate(string.text, locale)
            locale_string = LocaleString(
                id=string.id,
                locale=locale,
                text=translation['text'],
            )

            session.add(locale_string)

        elif with_update:
            translation = translate.translate(string.text, locale)
            target_string.text = translation['text']

    session.commit()
    session.close()

    print('Ok')
