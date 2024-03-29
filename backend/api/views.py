from django.db.models import Sum
from django.db.models.expressions import Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (AmountIngredient, FavoriteRecipe, Ingredient,
                            Recipe, ShoppingCart, Tag)
from users.models import Follow, User
from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (FavoriteOrShoppingRecipeSerializer, FollowSerializer,
                          IngredientSerializer, RecipesCreateSerializer,
                          RecipesListSerializer, TagSerializer, UserSerializer)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter, )
    queryset = Ingredient.objects.all()
    search_fields = ('^name',)
    pagination_class = None


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        methods=['GET'], detail=False, permission_classes=(IsAuthenticated,),
        pagination_class=PageLimitPagination,
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user.id == author.id:
                return Response(
                    {'errors': 'Вы не можете подписаться на себя!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                serializer = FollowSerializer(
                    Follow.objects.create(user=request.user, author=author),
                    context={'request': request},
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if Follow.objects.filter(
                user=request.user, author=author
            ).exists():
                Follow.objects.filter(
                    user=request.user, author=author
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': 'Автор отсутсвует в списке подписок'},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesListSerializer
        return RecipesCreateSerializer

    def get_queryset(self):
        qs = Recipe.objects.select_related('author').prefetch_related(
            'tags',
            'ingredients',
            'recipe',
            'shopping_cart_recipe',
            'favorite_recipe',
        )
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_favorited=Exists(
                    FavoriteRecipe.objects.filter(
                        user=self.request.user, recipe=OuterRef('id')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=self.request.user, recipe=OuterRef('id')
                    )
                ),
            )
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post_delete_recipe(self, request, pk, model):
        """Метод для добавления либо удаления рецепта из
        избранного/списка покупок в зависимости от указанной модели."""

        recipe_pk = self.kwargs.get('pk')
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        if request.method == 'POST':
            serializer = FavoriteOrShoppingRecipeSerializer(recipe)
            if model.objects.filter(
                    user=self.request.user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                model.objects.create(
                    user=self.request.user, recipe=recipe
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if model.objects.filter(
                user=self.request.user, recipe=recipe
            ).exists():
                model.objects.get(
                    user=self.request.user, recipe=recipe
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': 'Рецепт уже удален!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        return self.post_delete_recipe(
            request, self.kwargs.get('pk'), FavoriteRecipe)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
    )
    def shopping_cart(self, request, **kwargs):
        return self.post_delete_recipe(
            request, self.kwargs.get('pk'), ShoppingCart)

    @action(
        methods=['GET'], detail=False, permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = AmountIngredient.objects.select_related(
            'recipe', 'ingredient'
        )
        ingredients = ingredients.filter(
            recipe__shopping_cart_recipe__user=request.user
        )
        ingredients = ingredients.values(
            'ingredient__name', 'ingredient__measurement_unit'
        )
        ingredients = ingredients.annotate(ingredient_total=Sum('amount'))
        ingredients = ingredients.order_by('ingredient__name')
        shopping_list = 'Список покупок: \n'
        for ingredient in ingredients:
            shopping_list += (
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["ingredient_total"]} '
                f'({ingredient["ingredient__measurement_unit"]}) \n'
            )
            response = HttpResponse(
                shopping_list, content_type='text/plain; charset=utf8'
            )
            response[
                'Content-Disposition'
            ] = 'attachment; filename="shopping_list.txt"'
        return response
