from django.contrib import admin

from .models import Recipe, Tag, Ingredient

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'image', 'text', 'cooking_time']







