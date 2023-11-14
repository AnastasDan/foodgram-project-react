from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, Recipe, RecipeIngredient
from rest_framework import status
from rest_framework.response import Response


def add_or_remove_favorite_and_shopping_list(
    request, user, model, serializer, pk
):
    """Добавляет или удаляет рецепт из избранного или списка покупок."""
    if request.method == "POST":
        try:
            recipe = Recipe.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = serializer(
            data={"user": user.id, "recipe": recipe.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        model.objects.create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == "DELETE":
        recipe = get_object_or_404(Recipe, id=pk)

        recipe_delete = model.objects.filter(user=user, recipe=recipe)
        if not recipe_delete.exists():
            return Response(
                {"errors": "ошибка"}, status=status.HTTP_400_BAD_REQUEST
            )

        recipe_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def create_update_ingredients(recipe, ingredients_data):
    """Создает или обновляет ингредиенты для рецепта."""
    for ingredient_data in ingredients_data:
        ingredient_id = ingredient_data.get("id")
        amount = ingredient_data.get("amount")
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient, amount=amount
        )
