from flask_marshmallow import Marshmallow
from app import recipe_app
from app.db.model import User, Recipe, RecipeList

ma = Marshmallow(recipe_app)


class UserSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = User
        fields = ("id", "username", "name")


userSchema = UserSchema()
usersSchema = UserSchema(many=True)


class RecipeSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'url', 'user_id', 'recipe_list_id',
                  'recipe_list_name', 'ingredients', 'instructions',
                  'image_urls', 'time_created', 'views')


recipeSchema = RecipeSchema()
recipesSchema = RecipeSchema(many=True,
                             only=("id", "name", "ingredients", "instructions", "url", 'image_urls', 'views'))


class RecipeListSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = RecipeList
        fields = ("id", "name", "recipes")
    recipes = ma.Nested(recipesSchema)


recipeListSchema = RecipeListSchema()
recipeListsSchemaWithRecipes = RecipeListSchema(many=True)
recipeListsSchemaWithoutRecipes = RecipeListSchema(
    many=True, only=("id", "name"))
