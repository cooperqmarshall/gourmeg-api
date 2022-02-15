from msilib.schema import InstallUISequence
from flask import Response
from bs4 import BeautifulSoup
import requests
from model import Recipe


def validate_request(request, required_args):
    args_dict = {}
    for a in required_args:
        if request.json.get(a) is None:
            return Response(f'{{"field": {a}, "error": "{a} not found"}}',
                            status=401,
                            mimetype='application/json')
        args_dict[a] = request.json.get(a)
    return args_dict


def scrape_recipe_url(db, recipe_id, url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    # for EachPart in soup.select('div[class*="ingredients"]'):
    #     print(EachPart)
    ingredients = _remove_html_attrs(
        soup.select('div[class*="ingredients"]')[0])
    instructions = _remove_html_attrs(
        soup.select('div[class*="instructions"]')[0])
    ingredients.div.append(instructions)
    if ingredients(['iframe', 'script', 'input']):
        [s.extract() for s in ingredients(['iframe', 'script', 'input'])]
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    recipe.data = str(ingredients)
    recipe.name = soup.title.string
    db.session.commit()


def _remove_html_attrs(soup):
    tag_list = soup.find_all(lambda tag: len(tag.attrs) > 0)
    for tag in tag_list:
        tag.attrs = {}
    return soup


if __name__ == '__main__':
    scrape_recipe_url(
        'https://www.thechunkychef.com/family-favorite-baked-mac-and-cheese/')
