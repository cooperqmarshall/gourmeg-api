from flask.wrappers import Response
from bs4 import BeautifulSoup, Tag
import requests
import logging
import json

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


def get_ingredients_and_instructions_parent_tags(
    tag: Tag
) -> tuple[Tag | None,
           Tag | None]:

    num_ingredient_children, num_instruction_children = 0, 0
    ingredients_tag, instructions_tag = None, None

    for child in tag.contents:
        if type(child) == Tag and child.name != 'script':
            ingredients_tag_child, instructions_tag_child = get_ingredients_and_instructions_parent_tags(
                child)

            if ingredients_tag and instructions_tag:
                return ingredients_tag, instructions_tag

            if ingredients_tag_child is not None:
                num_ingredient_children += 1
                ingredients_tag = ingredients_tag_child

            if instructions_tag_child is not None:
                num_instruction_children += 1
                instructions_tag = instructions_tag_child

    # If `tag` contains > 1 ingredients/instructions tags then `tag` is assumed
    # to be the parent for the ingredients or instructions recipe content.
    if is_ingredient_tag(tag) or num_ingredient_children > 1:
        #log.debug(f'ingredient: {tag}')
        ingredients_tag = tag

    if is_instruction_tag(tag) or num_instruction_children > 1:
        #log.debug(f'instruction: {tag}')
        instructions_tag = tag

    # If the tag does not have any ingredient children, but is flagged as an
    # ingredient parent tag using an alternative criteria, then set `tag` as
    # the `ingredients_tag`. This is useful in cases such as with:
    # https://www.bonappetit.com/recipe/jammy-onion-and-miso-pasta where the
    # ingredients do not follow <ul> <li> format
    if ingredients_tag is None and is_ingredient_parent_tag(tag):
        #log.debug(f'ingredient: {tag}')
        ingredients_tag = tag

    return ingredients_tag, instructions_tag


def get_recipe_html(soup: BeautifulSoup
                    ) -> tuple[Tag | None,
                               Tag | None]:
    '''
    Find the nearest common ansestor tag that contains all tags above
    score_threshold
    '''
    if soup.body is None:
        return None, None

    ingredients_tag, instructions_tag = get_ingredients_and_instructions_parent_tags(
        soup.body)

    if ingredients_tag is None or instructions_tag is None:
        return None, None

    _clean_html(ingredients_tag, ['iframe', 'script', 'input', 'button'])
    _clean_html(instructions_tag, ['iframe', 'script', 'input', 'button'])

    return ingredients_tag, instructions_tag


def get_recipe_structured_data(soup: BeautifulSoup) -> tuple[list, list]:
    ldjson_tags = soup.find_all('script', {'type': 'application/ld+json'})
    data = [json.loads(tag.string) for tag in ldjson_tags]

    ingredients, structured_instructions = search_recipe_structured_data(data)

    instructions = []
    extract_structured_instructions_data(
        instructions,
        structured_instructions)
    # log.debug(ingredients)
    # log.debug(instructions)
    return ingredients, instructions


def search_recipe_structured_data(data: list):
    if not data:
        return [], []

    for item in data:
        if type(item) == list:
            ing, ins = search_recipe_structured_data(item)
            if ing and ins:
                return ing, ins

        ing = item.get("recipeIngredient")
        ins = item.get("recipeInstructions")
        if ing and ins:
            return ing, ins

        if item.get("@graph"):
            ing, ins = search_recipe_structured_data(item.get("@graph"))
            if ing and ins:
                return ing, ins

    return [], []


def extract_structured_instructions_data(instructions: list, structured_instructions: list):
    for item in structured_instructions:
        if type(item) == list:
            extract_structured_instructions_data(instructions, item)

        elif item.get("itemListElement"):
            extract_structured_instructions_data(
                instructions, item.get("itemListElement"))

        elif item.get("@type") == "HowToStep":
            instructions.append(item.get("text"))

    return instructions


def main_scrape(soup: BeautifulSoup) -> tuple[str, str]:
    '''
    Searches html for recipe ingredient and instructions data. Uses 2 methods
    for searching: First looks for recipe data in ldjson structured data in the
    head tag. Second, searches the html tree using depth first search for
    content that looks like ingredients or instructions based on certain
    criteria.

    params:
        soup: BeautifulSoup object of a recipe website

    returns:
        string of html formatted recipe ingredients 
        string of html formatted recipe instructions
    '''
    ingredients, instructions = get_recipe_structured_data(soup)
    if instructions and ingredients:
        ingredients_html = f"""<div><h3>Ingredients</h3><ul>{''.join([f'<li>{ingredient}</li>' for ingredient in ingredients])}</ul><div>"""
        instructions_html = f"""<div><h3>Instructions</h3><ol>{''.join([f'<li>{instruction}</li>' for instruction in instructions])}</ul></div>"""
        return ingredients_html, instructions_html

    instructions, ingredients = get_recipe_html(soup)
    if instructions and ingredients:
        return str(ingredients), str(instructions)

    return "", ""


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


def _clean_html(tag: Tag, remove_tags: list):
    _remove_html_attrs(tag)
    _remove_empty_tags(tag)
    _remove_tags(tag, remove_tags)


def _remove_html_attrs(parent_tag: Tag):
    [tag.attrs.clear() for tag in parent_tag.find_all() if tag.attrs]

    if parent_tag.attrs:
        parent_tag.attrs = {}

    return parent_tag


def _remove_empty_tags(parent_tag: Tag):
    [tag.extract() for tag in parent_tag.find_all()
     if len(tag.get_text(strip=True)) == 0]


def _remove_tags(tag: Tag, remove_tags: list):
    [t.extract() for t in tag(remove_tags)]
