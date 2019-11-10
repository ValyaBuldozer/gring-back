from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('config.py')
app.config.from_pyfile('db_config.py')
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, name='user_id')
    username = db.Column(db.String(100), name='user_name')
    password = db.Column(db.String(100), name='user_password')
    email = db.Column(db.String(200), name='user_email')

    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email


print('hi')
print(User.query.all())
