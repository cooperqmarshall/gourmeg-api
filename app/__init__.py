from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager, logout_user
from flask_migrate import Migrate
import os


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config[
    'SQLALCHEMY_ECHO'] = False  # os.environ['FLASK_ENV'] == 'development'

login_manager = LoginManager()
app.config['SESSION_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['REMEMBER_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = "Strict"
app.config['REMEMBER_COOKIE_SAMESITE'] = "Strict"
if os.environ['COOKIE_DOMAIN']:
    app.config['SESSION_COOKIE_DOMAIN'] = os.environ['COOKIE_DOMAIN']
    app.config['REMEMBER_COOKIE_DOMAIN'] = os.environ['COOKIE_DOMAIN']
login_manager.init_app(app)
app.secret_key = os.environ['SECRET_KEY']

# Objects

# fmt: off
from app.db.model import db
migrate = Migrate(app, db)
import app.api.routes
import app.db.schema
# fmt: on
