import os
import logging
from bs4 import BeautifulSoup
from app.utils.recipe_webscraper import get_recipe_structured_data, is_ingredient_tag, get_recipe_html, is_instruction_tag

log = logging.getLogger(__name__)

html = '''
<html>
<head>
</head>
<body>
test
<div class='ingredients'>
    <div>2 Eggs</div>
</div>
<div class='instructions'>
    <div>Stir</div>
    <div>Bake</div>
</div>
</body>
</html>
'''
soup = BeautifulSoup(html.replace('\n', ''), "html.parser")


def test_is_ingredient_tag():
    tag = soup.new_tag('li', attrs={'class': ''})
    assert not is_ingredient_tag(tag)

    tag = soup.new_tag('li', attrs={'class': ''})
    tag.string = ""
    assert not is_ingredient_tag(tag)

    tag = soup.new_tag('li', attrs={'class': 'container'})
    tag.string = "1 egg"
    assert is_ingredient_tag(tag)

    tag = soup.new_tag('li', attrs={'class': 'container ingredients'})
    tag.string = "1 egg"
    assert is_ingredient_tag(tag)

    tag = soup.new_tag('li', attrs={'class': 'Ingredient-wrapper'})
    tag.string = "1/2 egg"
    assert is_ingredient_tag(tag)

    tag = soup.new_tag('li', attrs={'class': 'content-wrapper'})
    tag.string = """1 thing about me is that when
    I was younger I liked to write Java.
    This was becasue it was a requirement for the class I was taking."""
    assert not is_ingredient_tag(tag)


def test_is_instructions_tag():
    tag = soup.new_tag('div', attrs={'class': 'instructions'})
    tag.string = ""
    assert not is_instruction_tag(tag)

    tag = soup.new_tag('li', attrs={'class': 'instructions'})
    tag.string = "Preheat the oven to 350"
    assert is_instruction_tag(tag)

    tag = soup.new_tag('li', attrs={'class': 'instructions'})
    tag.string = "Whisk to combine"
    assert is_instruction_tag(tag)


def test_get_recipe_html_simple(caplog):
    caplog.set_level(logging.DEBUG, logger='app.utils.recipe_webscraper')
    html = '''
    <html>
    <body>
    test
    <div class='ingredients'>
        <div>2 Eggs</div>
    </div>
    <div class='instructions'>
        <div>Stir</div>
        <div>Bake</div>
    </div>
    </body>
    </html>
    '''
    soup = BeautifulSoup(html.replace('\n', ''), "html.parser")
    ingredient_tag, instructions_tag = get_recipe_html(soup)

    html = '''
    <html>
    <body>
    <div class='ingredients'>
        Ingredients
        <ul>
            <li> <div>2 Eggs</div> </li>
            <li> <div>3 tablespoons <span>Milk</span></div> </li>
        </ul>
    </div>
    <div class='instructions'>
        <div>Stir</div>
        <div>Bake</div>
    </div>
    </body>
    </html>
    '''
    soup = BeautifulSoup(html.replace('\n', ''), "html.parser")
    get_recipe_html(soup)


def test_get_recipe_html_rwd():
    file_path = os.path.join(os.path.dirname(
        __file__), 'bon_appetit_onion_miso_pasta_raw.html')
    with open(file_path, 'r') as file:
        soup = BeautifulSoup(file.read(), "html.parser")
        ingredient_tag, instructions_tag = get_recipe_html(soup)
        response_recipe_html = (str(ingredient_tag) + str(instructions_tag))

    file_path = os.path.join(os.path.dirname(
        __file__), 'bon_appetit_onion_miso_pasta_clean.html')
    with open(file_path, 'r') as file:
        clean_recipe_html = file.read()

    assert response_recipe_html == clean_recipe_html.strip()
