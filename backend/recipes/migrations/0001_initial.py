import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_alter_subscription_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                    )
                 ),
                ('added', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Дата добавления списка'
                    )
                 ),
            ],
            options={
                'verbose_name': 'Рецепт в списке покупок',
                'verbose_name_plural': 'Рецепты в списке покупок',
                'ordering': ['-added'],
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('added', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Дата добавления рецепта'
                    )
                 ),
            ],
            options={
                'verbose_name': 'Избранный рецепт',
                'verbose_name_plural': 'Избранные рецепты',
                'ordering': ['-added'],
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                    )
                 ),
                ('name', models.CharField(
                    max_length=200,
                    verbose_name='Название'
                    )
                 ),
                ('measurement_unit', models.CharField(
                    max_length=200,
                    verbose_name='Единица измерения'
                    )
                 ),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='IngredientAmount',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                    )
                 ),
                ('amount', models.PositiveSmallIntegerField(
                    default=0,
                    validators=[
                        django.core.validators.MinValueValidator(
                            1,
                            'Ингредиента слишком мало!'
                            ),
                        django.core.validators.MaxValueValidator(
                            100000,
                            'Ингредиента слишком много!'
                            )
                        ]
                    )
                 ),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ['recipe'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                    )
                 ),
                ('name', models.CharField(
                    max_length=200,
                    validators=[
                        django.core.validators.MinLengthValidator(
                            limit_value=1,
                            message='У рецепта должно быть название!'
                            )
                        ],
                    verbose_name='Название'
                    )
                 ),
                ('image', models.ImageField(
                    upload_to='recipes/images/',
                    verbose_name='Изображение'
                    )
                 ),
                ('text', models.TextField(
                    verbose_name='Описание'
                    )
                 ),
                ('cooking_time', models.PositiveIntegerField(
                    validators=[
                        django.core.validators.MinValueValidator(
                            limit_value=1,
                            message='Минимальное время приготвления - 1 минута'
                            )
                        ],
                    verbose_name='Время приготовления'
                    )
                 ),
                ('published', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Дата публикации рецепта'
                    )
                 ),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['-published'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                    )
                 ),
                ('name', models.CharField(
                    max_length=200,
                    unique=True,
                    verbose_name='Название'
                    )
                 ),
                ('color', models.CharField(
                    max_length=7,
                    unique=True,
                    verbose_name='Цвет в HEX'
                    )
                 ),
                ('slug', models.SlugField(
                    max_length=200,
                    unique=True,
                    validators=[
                        django.core.validators.RegexValidator(
                            message=('Уникальный слаг содержит'
                                     ' недопустимый символ.'),
                            regex='^[-a-zA-Z0-9_]+$'
                            )
                        ],
                    verbose_name='Уникальный слаг'
                    )
                 ),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
                'ordering': ['name'],
            },
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(
                fields=('name', 'slug', 'color'),
                name='recipes_tag_name_slug_color_constraint'
                ),
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipes',
                to='users.user'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(
                related_name='recipes',
                through='recipes.IngredientAmount',
                to='recipes.Ingredient',
                verbose_name='Ингредиенты рецепта'
                ),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(
                related_name='recipes',
                to='recipes.Tag',
                verbose_name='Тэги'
                ),
        ),
        migrations.AddField(
            model_name='ingredientamount',
            name='ingredient',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='in_recipes',
                to='recipes.ingredient',
                verbose_name='Рецепты'
                ),
        ),
        migrations.AddField(
            model_name='ingredientamount',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='from_ingredients',
                to='recipes.recipe',
                verbose_name='Ингредиенты'
                ),
        ),
        migrations.AddField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='in_favorites',
                to='recipes.recipe',
                verbose_name='Избранные рецепты'
                ),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='favorites',
                to='users.user',
                verbose_name='Пользователь'
                ),
        ),
        migrations.AddField(
            model_name='cart',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='in_cart',
                to='recipes.recipe',
                verbose_name='Рецепты в списке покупок'
                ),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='cart_owner',
                to='users.user',
                verbose_name='Владелец списка покупок'
                ),
        ),
        migrations.AddConstraint(
            model_name='ingredientamount',
            constraint=models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='recipes_ingredientamount_recipe_ingr_constraint'
                ),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='recipes_favorite_recipe_user_constraint'
                ),
        ),
    ]
