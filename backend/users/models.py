from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from recipes.constants import REGEX


class MyUser(AbstractUser):
    """Модель пользователя, расширяющая AbstractUser."""

    email = models.EmailField("Почтовый адрес", max_length=254, unique=True)
    username = models.CharField(
        "Логин",
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(regex=REGEX, message="Недопустимый символ")
        ],
    )
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username


class Subscribe(models.Model):
    """Модель для представления подписок пользователей."""

    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Пользователь",
    )
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_user_author"
            )
        ]

    def __str__(self):
        """Возвращает строковое представление подписки."""
        return f"{self.user.username} подписан(а) на {self.author.username}"
