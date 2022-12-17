import logging
from bs4 import BeautifulSoup
from app.utils.recipe_webscraper import is_ingredient_tag, traverse_recipe_html


html = '''
<html>
<head>
</head>
<body>
<div>
Stir
</div>
</body>
</html>
'''


def test_calculate_ingredient_score(caplog):
    caplog.set_level(logging.DEBUG, logger='app.utils.recipe_webscraper')

    tag = soup.new_tag('li', attrs={'class': ''})
    assert is_ingredient_tag(tag) == 0

    tag = soup.new_tag('li', attrs={'class': ''})
    tag.string = ""
    assert is_ingredient_tag(tag) == 0

    tag = soup.new_tag('li', attrs={'class': 'container'})
    tag.string = "1 egg"
    assert is_ingredient_tag(tag) == 30

    tag = soup.new_tag('li', attrs={'class': 'container ingredients'})
    tag.string = "1 egg"
    assert is_ingredient_tag(tag) == 60

    tag = soup.new_tag('li', attrs={'class': 'Ingredient-wrapper'})
    tag.string = "1/2 egg"
    assert is_ingredient_tag(tag) == 60


