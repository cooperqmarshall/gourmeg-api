from flask.wrappers import Response
from bs4 import BeautifulSoup, Tag
import requests
import logging

log = logging.getLogger(__name__)


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


def calculate_ingredient_score(tag: Tag) -> int:
    score = (
        30 * tag_has_class(tag, 'ingredient') +
        30 * tag_content_begins_with_number(tag)
    )
    # log.debug(f'Tag {tag} ingredient score: {score}')
    return score


def tag_has_class(tag: Tag, class_name: str) -> bool:
    '''
    Checks if a Beauifulsoup Tag contains a given string in its class
    attribute.

    params
        tag: Beautifulsoup Tag object
        class_name: string to check 

    returns
        True if class_name is found in the tag's class attribute and false
        otherwise. 
    '''
    # log.debug("".join(tag['class']).lower())
    return tag.has_attr('class') and class_name in " ".join(tag['class']).lower()


def tag_content_begins_with_number(tag: Tag) -> bool:
    '''
    Checks if a Beautifulsoup Tag starts with a number. This function uses
    `isnumeric()` which includes fraction unicode chars compared to `isdigit()`
    or other number checking string helper functions which have different
    classifications for numbers.

    params
        tag: Beautifulsoup Tag object

    returns
        True if the first character in the Tag is a number. False if the first
        character is not a number or there is no content.
    '''
    # log.debug(tag.string)
    return tag.string is not None and len(tag.string) > 0 and tag.string[0].isnumeric()


def scrape_recipe_url(url):
    page = requests.get(url=url, headers={
                        "User-Agent": """Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0"""})
    soup = BeautifulSoup(page.content, "html.parser")
    # for EachPart in soup.select('div[class*="Ingredients"]'):
    #    print(EachPart)

    ingredient_classes = ['Ingredient', 'ingredient']
    ingredient_div = _search_attrs(soup, ingredient_classes)
    ingredients = _remove_html_attrs(ingredient_div)

    instruct_classes = ['instructions', 'Instructions', 'directions', 'Directions',
                        'Direction', 'Preparation', 'preparation', 'instruction', 'Instruction', 'steps', 'Steps']
    instruct_div = _search_attrs(soup, instruct_classes)
    instructions = _remove_html_attrs(instruct_div)

    imgs = [img for img in soup.find_all(
        'img') if 'src' in img.attrs.keys() and img['src'][0:4] == 'http']

    imgs.sort(key=lambda x: (int(x['width']) if 'width' in x.attrs.keys() and x['width'] != 'auto' else 100) * (
        int(x['height']) if 'height' in x.attrs.keys() and x['height'] != 'auto' else 100), reverse=True)
    imgs = [img['src'] for img in imgs]

    if ingredients(['iframe', 'script', 'input', 'button']):
        [s.extract() for s in ingredients(['iframe', 'script', 'input', 'button'])]
    if ingredients(['span']):
        [span.unwrap() for span in ingredients.findAll(['span'])]

    if instructions(['iframe', 'script', 'input', 'button']):
        [s.extract() for s in instructions(['iframe', 'script', 'input', 'button'])]
    if instructions(['span']):
        [span.unwrap() for span in instructions.findAll(['span'])]

    return {"name": soup.title.string, "ingredients": str(ingredients), "instructions": str(instructions), "imgs": imgs}


def _search_attrs(soup, search_list):
    for i in search_list:
        # print(soup.select(f'div[class*="{i}"]'))
        result_div = soup.select(f'section[class*="{i}"]')
        if result_div:
            return result_div[0]
        result_div = soup.select(f'div[class*="{i}"]')
        if result_div:
            return result_div[0]

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
