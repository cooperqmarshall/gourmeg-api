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


def test_get_recipe_structured_data():
    file_path = os.path.join(os.path.dirname(
        __file__), 'grinder_sandwitch_ldjson.html')
    with open(file_path, 'r') as file:
        soup = BeautifulSoup(file.read(), "html.parser")
        ing, ins = get_recipe_structured_data(soup)

    assert ing == [
        '½ head  iceberg lettuce',
        '½  small red onion',
        '1  pepperoncini (or 4-5 hot pepper rings)',
        '1  garlic clove',
        '2 tbsp mayonnaise (or greek yogurt)',
        '1 tbsp red wine vinegar',
        '2 tbsp parmesan cheese (grated)',
        '1/2 tsp Italian seasoning',
        '1/4 tsp oregano',
        '1/4 tsp chili flakes (optional)',
        'Pinch salt and pepper (to taste)',
        '2  Italian Style Hoagies (or submarine buns)',
        '1  medium beefsteak tomato (or tomato of choice)',
        '6 slices deli ham',
        '6 slices deli roasted turkey (or chicken)',
        '4 slices prosciutto',
        '8 slices capicolla (or salami of choice)',
        '8 slices Genoa salami (or salami of choice)',
        '6 slices provolone cheese (or mozzarella)',
        '2 tbsp parmesan cheese (grated)']
    assert ins == [
        'Prepare the salad ingredients. Shred the iceberg lettuce into thin strips. Thinly slice the red onion. Finely chop the pepperoncini pepper. Finely mince or grate the garlic clove.',
        'In a medium sized bowl combine the mayonnaise, red wine vinegar, parmesan cheese, Italian seasoning, oregano, chili flakes (if using). Mix until evenly combined.',
        'Add the lettuce, red onion, pepperoncini and garlic. Toss until evenly coated. Taste and season with salt and pepper as desired.',
        'Set aside in the fridge while you assemble the sandwich.',
        'Slice each hoagie or submarine bun through the centre and place on a sheet pan cut sides up.',
        'Place 3 slices of provolone cheese on the top half of each bun. Evenly distribute and layer the deli meat on the bottom halves.',
        'Place the sheet pan in the oven or toaster oven on ‘broil’ for 2-3 minutes, or until the cheese has melted (or air fry on 400°F for 2-3 minutes).',
        'Slice the tomato into thin slices and layer on top of the deli meat.',
        'Top with the grinder salad and sprinkle on the grated parmesan cheese.',
        'Close the sandwich and enjoy!']

    file_path = os.path.join(os.path.dirname(
        __file__), 'lavender_lemonade_ldjson.html')
    with open(file_path, 'r') as file:
        soup = BeautifulSoup(file.read(), "html.parser")
        ing, ins = get_recipe_structured_data(soup)

    assert ing == [
        '6 cups water (1,362 grams, divided)',
        '½ cup granulated sugar (100 grams)',
        '¼ cup honey (88 grams)',
        '3 tablespoons dried culinary lavender (1724)',
        '2 cups Freshly squeezed lemon juice (454 grams, from 10-12 lemons)',
        'Lemon slices (optional, for garnish)',
        'Lavender petals (optional, for garnish)',
        'Blue or purple food coloring (optional, to enhance color)']

    assert ins == [
        'Over medium heat, combine 2 cups of water and the sugar, bringing to a boil until the sugar is dissolved. Turn off the heat and stir in the honey and lavender.',
        'Allow the mixture to steep for 2 hours (less if you want less of a lavender taste).',
        'Strain the liquid, pressing the lavender down to make sure you get all of those juices into your mixture!',
        'In a large pitcher, combine freshly squeezed lemon juice, lavender mixture and the remaining 4 cups of water.',
        'Feel free to add a couple drops of blue or purple food coloring if you want more color than the lavender provides. Makes the lemonade especially cute for those brunches! Serve over ice.']
