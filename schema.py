from flask_marshmallow import Marshmallow
from app import app
from model import User, Recipe, RecipeList

ma = Marshmallow(app)


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
                  'recipe_list_name', 'data')


recipeSchema = RecipeSchema()
recipesSchema = RecipeSchema(many=True,
                             only=("id", "name", "recipe_list_name"))

class RecipeListSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = RecipeList
        fields = ("id", "name")


recipeListSchema = RecipeListSchema()
recipeListsSchema = RecipeListSchema(many=True)

