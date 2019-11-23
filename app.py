from flask import Flask, jsonify
from models.base import db
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import sessionmaker
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
from routes.objects import object_blueprint
from routes.routes import routes_blueprint
from routes.reviews import review_blueptint
from routes.places import place_blueptint
from routes.public_places import public_place_blueptint


app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('config.py')
app.config.from_pyfile('db_config.py')

app.register_blueprint(object_blueprint)
app.register_blueprint(routes_blueprint)
app.register_blueprint(review_blueptint)
app.register_blueprint(place_blueptint)
app.register_blueprint(public_place_blueptint)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=404, text=str(e)), 404


@app.errorhandler(400)
def invalid_request(e):
    return jsonify(error=400, text=str(e)), 400
