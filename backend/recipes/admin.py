from django.contrib import admin

from .models import Ingredient, Recipe, Tag
from users.models import User, Subscription


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'image', 'text', 'cooking_time']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'first_name',
        'last_name',
        'username'
    ]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'author_id',
        'user_id'
    ]
