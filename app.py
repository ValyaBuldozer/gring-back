from flask import Flask, jsonify, send_from_directory, request, abort
from models.base import db
from flask_jwt_extended import JWTManager
import os
import logging
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
from models.RoutePlaceInfo import RoutePlaceInfo
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
from routes.categories import category_blueprint
from util.osrm_client import osrm_init


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
app.register_blueprint(category_blueprint, url_prefix=api_url_prefix)

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()
    osrm_init()


@app.route(api_url_prefix + '/<path:path>')
def not_found_api(path):
    abort(404)
    return


@app.route('/assets/<path:path>', methods=['GET'])
def get_asset(path):
    return send_from_directory(app.config['ASSETS_PATH'], path)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_fe(path):
    path_dir = os.path.abspath(app.config['FE_BUILD_PATH'])

    if path != "" and os.path.exists(os.path.join(path_dir, path)):
        return send_from_directory(os.path.join(path_dir), path)
    else:
        return send_from_directory(os.path.join(path_dir), 'index.html')


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=404, text=str(e)), 404


@app.errorhandler(400)
def invalid_request(e):
    return jsonify(error=400, text=str(e)), 400


if __name__ == '__main__':
    logging.basicConfig(filename='gring.log', level=logging.DEBUG)
    app.run(host="0.0.0.0", port="5000")
