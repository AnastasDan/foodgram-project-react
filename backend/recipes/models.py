from django.core.validators import RegexValidator
from django.db import models

from users.models import MyUser

from .constants import REGEX


class Ingredient(models.Model):
    """Модель для представления ингредиентов."""

    name = models.CharField("Название", max_length=200)
    measurement_unit = models.CharField("Единица измерения", max_length=200)

    class Meta:
        ordering = ("id",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        """Возвращает строковое представление ингредиента."""
        return self.name


class Tag(models.Model):
    """Модель для представления тэгов."""

    name = models.CharField("Название тэга", max_length=200)
    color = models.CharField("Цвет", max_length=7)
    slug = models.SlugField(
        "Slug",
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(regex=REGEX, message="Недопустимый символ")
        ],
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        """Возвращает строковое представление тэга."""
        return self.name


class Recipe(models.Model):
    """Модель для представления рецептов."""

    tags = models.ManyToManyField(Tag, verbose_name="Тэг")
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient"
    )
    text = models.TextField("Описание")
    name = models.CharField("Название рецепта", max_length=200)
    image = models.ImageField("Фотография", upload_to="recipes/images/")
    cooking_time = models.IntegerField("Время приготовления")
    author = models.ForeignKey(
        MyUser,
        related_name="recipes",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        """Возвращает строковое представление рецепта."""
        return self.name


class RecipeIngredient(models.Model):
    """Модель для представления ингредиентов в рецептах."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="Ингредиент",
    )
    amount = models.IntegerField("Количество")

    class Meta:
        verbose_name = "Ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецепта"

    def __str__(self):
        """Возвращает строковое представление ингредиента для рецепта."""
        return self.recipe.name


class FavoriteRecipe(models.Model):
    """Модель для представления избранных рецептов."""

    user = models.ForeignKey(
        MyUser,
        related_name="favorite_recipes",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="favorited_by",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_favorite_recipe"
            )
        ]

    def __str__(self):
        """Возвращает строковое представление избранного рецепта."""
        return self.recipe.name


class ShoppingList(models.Model):
    """Модель для представления списков покупок."""

    user = models.ForeignKey(
        MyUser,
        related_name="shopping_lists",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="in_shopping_lists",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_shopping_list"
            )
        ]

    def __str__(self):
        """Возвращает строковое представление списка покупок."""
        return self.recipe.name
