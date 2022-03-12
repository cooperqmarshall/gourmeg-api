from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import VARCHAR, Column, String, Integer, DateTime, Text, func, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from app import app

db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = 'User'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    passwordHash = Column(String)
    name = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    recipes = relationship('Recipe', backref="user")
    recipe_lists = relationship('RecipeList', backref='user')


class Recipe(db.Model):
    __tablename__ = 'Recipe'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'))
    recipe_list_id = Column(Integer, ForeignKey('RecipeList.id'))
    recipe_list_name = Column(String)
    recipe_list = relationship('RecipeList', backref='recipes')
    name = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    url = Column(String)
    data = Column(Text)


class RecipeList(db.Model):
    __tablename__ = 'RecipeList'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    name = Column(String)
    user_id = Column(Integer, ForeignKey('User.id'))

