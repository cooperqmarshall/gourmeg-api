from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
import os


recipe_app = Flask(__name__)
CORS(recipe_app, supports_credentials=True)
recipe_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
recipe_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
recipe_app.config['SQLALCHEMY_ECHO'] = False

login_manager = LoginManager()
recipe_app.config['SESSION_COOKIE_SECURE'] = False
recipe_app.config['REMEMBER_COOKIE_SECURE'] = False
recipe_app.config['SESSION_COOKIE_HTTPONLY'] = False
recipe_app.config['REMEMBER_COOKIE_HTTPONLY'] = False
recipe_app.config['SESSION_COOKIE_SAMESITE'] = "Strict"
recipe_app.config['REMEMBER_COOKIE_SAMESITE'] = "Strict"
if os.environ['COOKIE_DOMAIN']:
    recipe_app.config['SESSION_COOKIE_DOMAIN'] = os.environ['COOKIE_DOMAIN']
    recipe_app.config['REMEMBER_COOKIE_DOMAIN'] = os.environ['COOKIE_DOMAIN']
login_manager.init_app(recipe_app)
recipe_app.secret_key = os.environ['SECRET_KEY']

# fmt: off
from app.db.model import db
migrate = Migrate(recipe_app, db)
import app.api.routes_v1
import app.api.routes_v2
import app.db.schema
# fmt: on
