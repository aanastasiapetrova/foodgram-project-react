from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=254,
                              unique=True,
                              verbose_name='Email пользователя'
                              )
    username = models.CharField(max_length=150,
                                unique=True,
                                db_index=True,
                                verbose_name='Имя пользователя'
                                )
    first_name = models.CharField(max_length=150,
                                  verbose_name="Имя"
                                  )
    last_name = models.CharField(max_length=150,
                                 verbose_name='Фамилия'
                                 )
    password = models.CharField(max_length=150,
                                verbose_name='Пароль'
                                )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен"
    )

    class Meta:
        verbose_name = ("Пользователь")
        verbose_name_plural = ("Пользователи")

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribefor'
    )

    class Meta:
        verbose_name = ("Подписка")
        verbose_name_plural = ("Подписки")
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='%(app_label)s_%(class)s_author_user_constraint'
            ),
        )
