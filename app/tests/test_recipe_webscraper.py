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


