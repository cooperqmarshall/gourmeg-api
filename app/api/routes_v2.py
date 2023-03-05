from bs4 import BeautifulSoup
from flask import request
from marshmallow.exceptions import ValidationError
import requests
from requests.exceptions import RequestException
from app.db.schema import recipeSchema, recipesSchema
from app.db.model import db, Recipe, RecipeList, User
from flask_login import current_user, login_required
from app import recipe_app

import logging

log = logging.getLogger(__name__)

from app.utils.recipe_webscraper import main_scrape, scrape_recipe_image


@login_required
def post_recipe():
    try:
        args = recipeSchema.load(request.json) 
    except ValidationError as error: 
        return {"error": error.messages_dict}, 400
    print(args)

    recipe = Recipe(url=args['url'],
                    user_id=current_user.id,
                    recipe_list_name=args['recipe_list_name'])

    # TODO: use existing recipe in database if found
    try:
        res = requests.get(args['url'], headers={
                    "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"""})
    except RequestException as error:
        return {"error": str(error)}, 400
    
    soup = BeautifulSoup(res.content, 'html.parser')

    ingredients, instructions = main_scrape(soup)

    if not ingredients or not instructions:
        return {"error": f"unable to extract recipe information from {args['url']}"}, 400

    recipe.ingredients = ingredients
    recipe.instructions = instructions

    # TODO: use og meta tags or ldjson
    recipe.name = soup.title.string

    # TODO: use ldjson for image urls
    recipe.image_urls = scrape_recipe_image(soup)

    recipe_list = RecipeList.query.filter(
        RecipeList.name == args['recipe_list_name']).join(
            RecipeList.user).filter(User.id == current_user.id).first()
    if not recipe_list:
        log.info('no recipe list: {args["recipe_list_name"}. Will create new list.')
        recipe_list = RecipeList(name=args['recipe_list_name'])
        current_user.recipe_lists.append(recipe_list)

    recipe_list.recipes.append(recipe)

    db.session.add(recipe_list)
    db.session.commit()
    db.session.refresh(recipe)
    
    return recipeSchema.dump(recipe)


def search():
    search_term = request.args.get('term')

    if search_term is None or search_term == '':
        return {"error": "please supply a search term"}, 400

    print(search_term)
    recipes = Recipe.query.filter(Recipe.name.ilike(f'%%{search_term}%%')).all()

    return {"recipes": recipesSchema.dump(recipes)}


recipe_app.add_url_rule("/api/v2/recipe", view_func=post_recipe, methods=["POST"])
recipe_app.add_url_rule("/api/v2/search", view_func=search, methods=["GET"])
