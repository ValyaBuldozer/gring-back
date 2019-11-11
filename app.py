from flask import Flask
from models.base import db
from models.Category import Category
from models.City import City
from models.Object import Object
from models.CategoryObject import CategoryObject
from models.Geolocation import Geolocation
from models.Place import Place
from models.PublicPlace import PublicPlace
from models.Timetable import Timetable
from models.HistoricalPerson import HistoricalPerson
from models.HistoricalPersonRelatedObjects import HistoricalPersonRelatedObjects
from models.Route import Route
from models.RouteObjectInfo import RouteObjectInfo
from models.User import User
from models.Review import Review
from models.Role import Role
from models.UserRole import UserRole


app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('config.py')
app.config.from_pyfile('db_config.py')

db.init_app(app)

with app.app_context():
    db.create_all()
    print(Object.query.all())


print('app started')
