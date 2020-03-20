from models.base import db
from models.Language import Language


class LocaleLink(db.Model):

    __tablename__ = "locale_link"
    id = db.Column(
        db.String(36),
        primary_key=True,
        name="link_id",
        nullable=False
    )
    locale = db.Column(
        db.Enum(Language),
        primary_key=True,
        name="link_locale",
        nullable=False
    )
    path = db.Column(
        db.Text,
        name="link_path",
        nullable=False
    )

    def to_json(self, locale):
        return self.path

