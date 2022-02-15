from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager, logout_user
from flask_migrate import Migrate
import os

# TODO
'''
Recipe randomizer
cat logo
url to add Recipe
hello after sign in
mouse cookie (or pizza or some food or snack)
password reset, show password and confirm
food picture
better colors ... pazzaz
name (Gourmeg)
insert picutres and start
'''

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config[
    'SQLALCHEMY_ECHO'] = False  # os.environ['FLASK_ENV'] == 'development'

login_manager = LoginManager()
app.config['SESSION_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = "Strict"
app.config['REMEMBER_COOKIE_SAMESITE'] = "Strict"
login_manager.init_app(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # TODO change later!

# Objects
from model import db

migrate = Migrate(app, db)

# Schema
import schema

# Routes
import routes

if __name__ == '__main__':
    app.run(debug=os.environ['FLASK_ENV'] == 'development')
