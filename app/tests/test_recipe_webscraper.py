from bs4 import BeautifulSoup
from app.utils.recipe_webscraper import calculate_ingredient_score


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


soup = BeautifulSoup(html, "html.parser")


def test_calculate_ingredient_score():
    tag = soup.new_tag('li', attrs={'class': ''})
    tag.string = ""
    assert calculate_ingredient_score(tag) == 0

    tag = soup.new_tag('li', attrs={'class': 'container'})
    tag.string = "1 egg"
    assert calculate_ingredient_score(tag) == 30

    tag = soup.new_tag('li', attrs={'class': 'ingredients'})
    tag.string = "1 egg"
    assert calculate_ingredient_score(tag) == 60
