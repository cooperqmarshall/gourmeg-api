from app import app, login_manager
from model import db, User, Recipe, RecipeList
from schema import userSchema, recipesSchema, recipeSchema
from passlib.hash import argon2
from flask import request, Response
from flask_login import login_user, login_required, current_user
from datetime import timedelta
from utils import validate_request, scrape_recipe_url
import threading


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.get('/api/v1/user/<int:id>')
def user(id):
    user = User.query.get_or_404(id,
                                 description=f'There is no user with id: {id}')
    return userSchema.dump(user)


@app.get('/api/v1/user/<string:username>')
def username(username):
    user = User.query.filter_by(username=username).first()
    return userSchema.dump(user) if user else Response(
        f'{{"field": "username", "error": "There is no user with username: {username}"}}',
        status=401,
        mimetype='application/json')


@app.post('/api/v1/register')
def register():
    args = validate_request(request, ['username', 'password'])
    if type(args) is Response:
        return args
    if len(args['username']) < 2 or len(args['username']) > 30:
        return Response(
            '{"field": "username", "error": "username must be between 2 and 30 characters"}',
            status=401,
            mimetype='application/json')
    if len(args['password']) < 2 or len(args['password']) > 30:
        return Response(
            '{"field": "password", "error": "password must be between 2 and 30 characters"}',
            status=401,
            mimetype='application/json')

    if (User.query.filter_by(username=args['username']).first()):
        return Response(
            '{"field": "username", "error": "username already taken"}',
            status=409,
            mimetype='application/json')

    user = User(username=args['username'],
                passwordHash=argon2.hash(args['password']))
    db.session.add(user)
    db.session.flush()
    db.session.refresh(user)
    db.session.commit()
    return userSchema.dump(user)


@app.post('/api/v1/signin')
def signin():
    args = validate_request(request, ['username', 'password'])
    if type(args) is Response:
        return args

    user = User.query.filter_by(username=args['username']).first()
    if (user is None):
        return Response(
            f'{{"field": "username", "error": "There is no user with username: {args["username"]}"}}',
            status=401,
            mimetype='application/json')

    if (not argon2.verify(args['password'], user.passwordHash)):
        return Response('{"field": "password", "error": "incorrect password"}',
                        status=401,
                        mimetype='application/json')

    login_user(user, remember=True, duration=timedelta(days=100))
    return userSchema.dump(user)


@app.get('/api/v1/me')
@login_required
def me():
    return userSchema.dump(current_user)


@app.get('/api/v1/recipes')
@login_required
def recipes():
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    return {"recipes": recipesSchema.dump(recipes)}


@app.post('/api/v1/recipe')
@login_required
def add_recipe():
    args = validate_request(request, ['list', 'url'])
    if type(args) is Response:
        return args
    recipe = Recipe(url=args['url'],
                    user_id=current_user.id,
                    recipe_list_name=args['list'])
    recipe_list = RecipeList.query.filter(
        RecipeList.name == args['list']).join(
            RecipeList.user).filter(User.id == current_user.id).first()
    if not recipe_list:
        print('no list')
        recipe_list = RecipeList(name=args['list'])
        current_user.recipe_lists.append(recipe_list)
    recipe_list.recipes.append(recipe)
    db.session.add(recipe_list)
    db.session.commit()
    db.session.refresh(recipe)
    x = threading.Thread(target=scrape_recipe_url,
                         args=(db, recipe.id, args['url']))
    x.start()
    return recipeSchema.dump(recipe)