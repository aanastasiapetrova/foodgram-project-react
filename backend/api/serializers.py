from recipes.models import *
from users.models import *
from rest_framework.serializers import ModelSerializer

User = get_user_model()

class RecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'