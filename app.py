from flask import Flask
from models.base import db
from models.Place import Place

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('config.py')
app.config.from_pyfile('db_config.py')

db.init_app(app)

with app.app_context():
    db.create_all()
    print(Place.query.all())


print('app started')
