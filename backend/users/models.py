from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class MyUser(AbstractUser):
    email = models.EmailField('Почтовый адрес', max_length=254, unique=True)
    username = models.CharField('Логин', max_length=150, unique=True, validators=[
            RegexValidator(regex=r"^[\w.@+-]+$", message="Недопустимый символ")
        ],
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

class Subscribe(models.Model): 
    user = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name="followers", verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name="following", verbose_name='Автор'
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
        return self.user.username