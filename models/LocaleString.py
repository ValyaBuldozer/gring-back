from models.base import db
from models.Language import Language


class LocaleString(db.Model):

    __tablename__ = "locale_string"
    id = db.Column(
        db.String(36),
        primary_key=True,
        name="string_id",
        nullable=False
    )
    locale = db.Column(
        db.Enum(Language),
        primary_key=True,
        name="string_locale",
        nullable=False
    )
    text = db.Column(
        db.Text,
        name="string_content",
        nullable=False
    )

    def to_json(self, locale):
        return self.text

