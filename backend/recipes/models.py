from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator, RegexValidator)
from django.db import models
from PIL import Image

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название',
        unique=True
    )
    color = models.CharField(
        max_length=7,
        blank=False,
        verbose_name='Цвет в HEX',
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        validators=[RegexValidator(
            regex='^[-a-zA-Z0-9_]+$',
            message='Уникальный слаг содержит недопустимый символ.')],
        blank=False,
        verbose_name='Уникальный слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['name',]
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'slug', 'color'),
                name='%(app_label)s_%(class)s_name_slug_color_constraint'
            ),
        )


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name', ]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        blank=False,
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название',
        validators=[
            MinLengthValidator(
                limit_value=1,
                message='У рецепта должно быть название!'
            ),
        ]
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
        verbose_name='Изображение'
    )
    text = models.TextField(
        blank=False,
        verbose_name='Описание'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(
                    limit_value=1,
                    message='Минимальное время приготвления - 1 минута')],
        blank=False,
        verbose_name='Время приготовления'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='recipes.IngredientAmount',
        related_name='recipes',
        verbose_name='Ингредиенты рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги'
    )
    published = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='Дата публикации рецепта')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-published', ]

    def __str__(self) -> str:
        return self.name

    def clean(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.img.path)
        img.thumbnail([100, 100])
        img.save(self.img.path)


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favorites',
        verbose_name='Избранные рецепты',
        on_delete=models.CASCADE
    )
    added = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='Дата добавления рецепта'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['-added', ]
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='%(app_label)s_%(class)s_recipe_user_constraint'
            ),
        )


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='in_recipes',
        verbose_name='Рецепты',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='from_ingredients',
        verbose_name='Ингредиенты',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        default=0,
        validators=(
            MinValueValidator(
                1,
                'Ингредиента слишком мало!'
            ),
            MaxValueValidator(
                10**5,
                'Ингредиента слишком много!'
            )
        )
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['recipe']
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='%(app_label)s_%(class)s_recipe_ingr_constraint'
            ),
        )


class Cart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_cart',
        verbose_name='Рецепты в списке покупок',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        related_name='cart_owner',
        verbose_name='Владелец списка покупок',
        on_delete=models.CASCADE,
    )
    added = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='Дата добавления списка'
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        ordering = ['-added', ]
