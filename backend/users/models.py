from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    email = models.EmailField(max_length=254,
                              unique=True,
                              verbose_name='Email пользователя'
                              )
    username = models.CharField(max_length=150,
                                unique=True,
                                db_index=True,
                                #validators=[
                                #    RegexValidator(regex=r'^[\w.@+-]+\z',
                                #                   message='Имя пользователя содержит недопустимый символ.')
                                #           ],
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

    

class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscibefor'
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

    

    
