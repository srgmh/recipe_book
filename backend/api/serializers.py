from drf_base64.fields import Base64ImageField
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from rest_framework.serializers import (BooleanField, CurrentUserDefault,
                                        IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)
from users.models import Follow, User


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(user=user, author=obj).exists()


class AmountIngredientSerializer(ModelSerializer):
    id = ReadOnlyField(source="ingredient.id")
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = AmountIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class AddAmountIngredientSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField()

    class Meta:
        model = AmountIngredient
        fields = (
            "id",
            "amount",
        )


class RecipesListSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(
        read_only=True, default=CurrentUserDefault()
    )
    ingredients = AmountIngredientSerializer(
        many=True, required=True, source="recipe"
    )
    is_favorited = BooleanField(read_only=True)
    is_in_shopping_cart = BooleanField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class RecipesCreateSerializer(ModelSerializer):
    ingredients = AddAmountIngredientSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = "__all__"
        read_only_fields = ("author",)

    def validate(self, data):
        ingredients = data["ingredients"]
        unique_set = set()
        for ingredient_data in ingredients:
            current_ingredient = ingredient_data["id"]
            if current_ingredient in unique_set:
                raise ValidationError(
                    "В списке ингредиентов - два одинаковых значения."
                    " Проверьте состав."
                )
            unique_set.add(current_ingredient)
        return data

    def create_amount_ingredients(self, ingredients, recipe):
        AmountIngredient.objects.bulk_create(
            [AmountIngredient(
                recipe=recipe,
                ingredient=ingredient.get("id"),
                amount=ingredient.get("amount"),
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.create_amount_ingredients(ingredients, recipe)
        return recipe

    def update(self, obj, validated_data):
        if "ingredients" in validated_data:
            ingredients = validated_data.pop("ingredients")
            obj.ingredients.clear()
            self.create_amount_ingredients(ingredients, obj)
        if "tags" in validated_data:
            tags = validated_data.pop("tags")
            obj.tags.set(tags)
        return super().update(obj, validated_data)

    def to_representation(self, instance):
        serializer = RecipesListSerializer(instance)
        return serializer.data


class FavoriteOrShoppingRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FollowSerializer(ModelSerializer):
    email = ReadOnlyField(source="author.email")
    id = ReadOnlyField(source="author.id")
    username = ReadOnlyField(source="author.username")
    first_name = ReadOnlyField(source="author.first_name")
    last_name = ReadOnlyField(source="author.last_name")
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author).order_by(
            "-pub_date"
        )
        return FavoriteOrShoppingRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
