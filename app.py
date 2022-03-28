# Routes
import routes

# Schema
import schema

from model import db
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
    'SQLALCHEMY_ECHO'] = os.environ['FLASK_ENV'] == 'development'

login_manager = LoginManager()
app.config['SESSION_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = "Strict"
app.config['REMEMBER_COOKIE_SAMESITE'] = "Strict"
login_manager.init_app(app)
app.secret_key = os.environ['SECRET_KEY']

# Objects

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=os.environ['FLASK_ENV'] == 'development')
