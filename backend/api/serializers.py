from recipes.models import (
    Tag,
    Ingredient,
    IngredientAmount,
    Recipe
)
from users.models import User
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from django.db.transaction import atomic


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        read_only_fields = ('is_subscribed',)
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def get_is_subscribed(self, author):
        user = self.context['request'].user

        if user.is_anonymous or (user == author):
            return False

        return user.subscriber.filter(author=author).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            'is_favorited',
            'is_in_shopping_cart',
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            'is_favorited',
            'is_in_shopping_cart',
        )

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        if not tags or not ingredients:
            raise Exception('Вы не ввели ингредиенты или тэги')

        data.update(
            {
                'tags': tags,
                'ingredients': ingredients,
                'author': self.context.get('request').user,
            }
        )

        return data

    @atomic
    def create(self, validated_data):
        ingredient_amount = []
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient_info in ingredients:
            ingredient_id = int(ingredient_info['id'])
            print(Ingredient.objects.get(pk=ingredient_id))
            ingredient_am = int(ingredient_info['amount'])
            if Ingredient.objects.filter(pk=ingredient_id).exists():
                ingredient_amount.append(
                    IngredientAmount(
                        recipe=Recipe.objects.get(pk=recipe.pk),
                        ingredient=Ingredient.objects.get(pk=ingredient_id),
                        amount=ingredient_am
                    )
                )
        IngredientAmount.objects.bulk_create(ingredient_amount)
        recipe.save()

        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredient_amount = []
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        for key, value in validated_data.items():
            if getattr(instance, key) != value:
                setattr(instance, key, value)

        instance.tags.set(tags)
        instance.ingredients.clear()

        for ingredient_info in ingredients:
            ingredient_amount = IngredientAmount.objects.create(
                recipe_id=instance.id,
                ingredient_id=ingredient_info['id'],
                amount=ingredient_info['amount']
            )
            ingredient_amount.save()

        instance.save()
        return instance

    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('in_recipes__amount')
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('view').request.user

        if user.is_anonymous:
            return False

        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('view').request.user

        if user.is_anonymous:
            return True

        return user.cart_owner.filter(recipe=recipe).exists()


class PreviewRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = ("__all__",)

    def get_is_subscribed(self, author):
        return True

    def get_recipes(self, user):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=user.id)

        if limit:
            recipes = recipes[:int(limit)]
        return PreviewRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, user):
        return user.recipes.count()
