from flask import Flask, jsonify, send_from_directory, request, abort
from models.base import db
from flask_jwt_extended import JWTManager
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
from routes.auth import auth_blueprint
from routes.objects import object_blueprint
from routes.routes import routes_blueprint
from routes.reviews import review_blueptint
from routes.places import place_blueptint
from routes.public_places import public_place_blueptint
from routes.historical_persons import historical_person_blueptint


app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('config.py')
# db config + secret key
app.config.from_pyfile('secret_config.py')

api_url_prefix = app.config['API_URL_PREFIX']
app.register_blueprint(auth_blueprint, url_prefix=api_url_prefix)
app.register_blueprint(object_blueprint, url_prefix=api_url_prefix)
app.register_blueprint(routes_blueprint, url_prefix=api_url_prefix)
app.register_blueprint(review_blueptint, url_prefix=api_url_prefix)
app.register_blueprint(place_blueptint, url_prefix=api_url_prefix)
app.register_blueprint(public_place_blueptint, url_prefix=api_url_prefix)
app.register_blueprint(historical_person_blueptint, url_prefix=api_url_prefix)

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=404, text=str(e)), 404


@app.errorhandler(400)
def invalid_request(e):
    return jsonify(error=400, text=str(e)), 400


@app.route('/assets/<path:path>', methods=['GET'])
def get_asset(path):
    return send_from_directory(app.config['ASSETS_PATH'], path)


if __name__ == '__main__':
    logging.basicConfig(filename='gring.log', level=logging.DEBUG)
    app.run(host="0.0.0.0", port="5000")
