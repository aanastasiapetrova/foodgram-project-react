from recipes.models import *
from users.models import *
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

User = get_user_model()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        
        
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        
        
class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientSerializer(read_only=True, many=True)
    image = Base64ImageField()
    is_favorite = serializers.SerializerMethodField(method_name='get_is_favorite')
    is_in_shopping_cart = serializers.SerializerMethodField(method_name='get_is_in_shopping_cart')
    
    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            'is_favorite', 
            'is_in_shopping_cart',
                 )
        read_only_fields = (
            'is_favorite', 
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
                #'author': self.context.get('request').user,
                'author': User.objects.get(pk=1)
            }
        )
        
        return data
        
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
                ingredient_amount.append(IngredientAmount(recipe=Recipe.objects.get(pk=recipe.pk), ingredient=Ingredient.objects.get(pk=ingredient_id), amount=ingredient_am))
        IngredientAmount.objects.bulk_create(ingredient_amount)
        recipe.save()
        
        return recipe
    
    def get_is_favorite(self, recipe):
        user = self.context.get('view').request.user
        
        if user.is_anonymous:
            return False
        
        return user.favorites.filter(recipe=recipe).exists()
    
    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('view').request.user
        
        if user.is_anonymous:
            return True
        
        return user.cart_owner.filter(recipe=recipe).exists()


class UserSerializer(serializers.ModelSerializer):    
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')
        extra_kwargs = {
            "password": {"write_only": True},
        }
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        return user
 
 
