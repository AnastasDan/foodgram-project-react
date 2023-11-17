from django.db import models
from django.db.models import Case, When


class RecipeQuerySet(models.QuerySet):
    """QuerySet для модели Recipe."""

    def favorited(self, user):
        """Аннотирует queryset полем is_favorited."""
        return self.annotate(
            is_favorited=Case(
                models.When(favorited_by__user=user, then=True),
                default=False,
            )
        )

    def in_shopping_cart(self, user):
        """Аннотирует queryset полем is_in_shopping_cart."""
        return self.annotate(
            is_in_shopping_cart=models.Case(
                When(in_shopping_lists__user=user, then=True),
                default=False,
            )
        )


class RecipeManager(models.Manager):
    """Менеджер для модели Recipe."""

    def get_queryset(self):
        """Возвращает queryset для менеджера рецептов."""
        return RecipeQuerySet(self.model, using=self._db)

    def favorited(self, user):
        """Возвращает аннотированный queryset с флагом is_favorited."""
        return self.get_queryset().favorited(user)

    def in_shopping_cart(self, user):
        """Возвращает аннотированный queryset с флагом is_in_shopping_cart."""
        return self.get_queryset().in_shopping_cart(user)
