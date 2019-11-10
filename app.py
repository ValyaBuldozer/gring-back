from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.base import db
from models.Category import Category
from models.City import City
from models.Object import Object

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('config.py')
app.config.from_pyfile('db_config.py')

db.init_app(app)

with app.app_context():
    db.create_all()
    print(Object.query.all())


print('app started')
