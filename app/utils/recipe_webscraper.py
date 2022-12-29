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


def is_ingredient_tag(tag: Tag, score_threshold: int = 4) -> bool:
    content = tag.get_text().strip()
    if len(content) == 0 or tag_has_class(tag, ["rating", "nav", "social"]):
        return False

    score = [
        content[0].isnumeric(),
        any(c.isalpha() for c in content),
        (len(content) < 100),
        # nice to have
        tag_has_class(tag, 'ingredient'),
        (tag.name in ["li"])
    ]

    return sum(score) >= score_threshold


def is_ingredient_parent_tag(tag: Tag) -> bool:
    content = tag.get_text().strip()
    if len(content) == 0 or tag_has_class(tag, ["rating", "nav", "social"]):
        return False

    return (len(content) > 50
            and "ingredient" in content.split()[0].lower()
            and sum([any(char.isnumeric() for char in word) for word in content.split()]) > 2
            and tag.name in ["div", "ul"])


def tag_has_class(tag: Tag, class_name: str | list[str]) -> bool:
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
    if not tag.has_attr('class'):
        return False
    if type(class_name) == str:
        class_name = [class_name]

    tag_class = " ".join(tag['class']).lower()
    return any([c in tag_class for c in class_name])


def is_instruction_tag(tag: Tag, score_threshold: int = 3) -> int:
    content = tag.get_text().strip()
    if len(content) == 0:
        return False

    first_words = [sentance.strip().split()[0]
                   for sentance in content.split(".") if sentance.strip()]

    score = [
        any(word.lower() in ["bake", "stir", "preheat", "whisk", "dice", "prepair", "boil", "chop", "mix", "add", "heat", "pour"]
            for word in first_words),
        ((10 < len(content) < 650)
         or (0 < len(first_words) < 8)),
        # nice to have
        tag_has_class(tag, ['instruction', "direction", "step"]),
        tag.name in ["li"]
    ]

    # log.debug(f'Tag {tag} ingredient score: {sum(score)}')
    return sum(score) >= score_threshold

    '''


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
