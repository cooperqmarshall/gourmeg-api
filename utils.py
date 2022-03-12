from flask.wrappers import Response
from bs4 import BeautifulSoup
import requests
from requests.models import MissingSchema
from model import Recipe


def validate_request(request, required_args, query=False):
    args_dict = {}
    for a in required_args:
        arg = request.json.get(a) if not query else request.args.get(a)
        if not arg:
            return Response(f'{{"field": "{a}", "error": "{a} not found"}}',
                            status=401,
                            mimetype='application/json')
        args_dict[a] = arg
    return args_dict


def scrape_recipe_url(db, url):
    page = requests.get(url=url, headers={"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0"})
    soup = BeautifulSoup(page.content, "html.parser")
    # for EachPart in soup.select('div[class*="Ingredients"]'):
    #    print(EachPart)

    ingredient_classes = ['Ingredient', 'ingredient']
    ingredient_div = _search_attrs(soup, ingredient_classes)
    ingredients = _remove_html_attrs(ingredient_div)

    instruct_classes = ['instruction', 'Instruction', 'step', 'direction', 'how', 'Preparation']
    instruct_div = _search_attrs(soup, instruct_classes)
    instructs = _remove_html_attrs(instruct_div)
    ingredients.append(instructs)

    if ingredients(['iframe', 'script', 'input']):
        [s.extract() for s in ingredients(['iframe', 'script', 'input'])]
    return soup.title.string, str(ingredients)

def _search_attrs(soup, search_list):
    for i in search_list:
        # print(soup.select(f'div[class*="{i}"]'))
        result_div = soup.select(f'div[class*="{i}"]')
        if result_div: return result_div[0]

    for div in soup.find_all('div'):
        for attr, val in div.attrs.items():
            if attr != 'class':
                if any(string in val for string in search_list):
                    return div


def _remove_html_attrs(soup):
    tag_list = soup.find_all(lambda tag: len(tag.attrs) > 0)
    for tag in tag_list:
        tag.attrs = {}
    return soup

