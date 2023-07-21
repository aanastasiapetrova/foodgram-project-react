from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .mixins import *
from users.models import User
from recipes.models import *
from rest_framework.response import Response
from rest_framework.decorators import action


class UserViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    

class RecipeViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all() 
    
    @action(detail=True)
    def favorites(self, request, pk=None):
        #return Response({'status': 'Выполнился экшн'}
        pass
    
    @favorites.mapping.post
    def add_to_favorites(self, request, pk=None):
        return Response({'status': 'favorites mapping post'})
    
    @favorites.mapping.delete
    def delete_from_favorites(self, request, pk=None):
        return Response({'status': 'favorites mapping delete'})
    
    @action(detail=True, methods=['get'])
    def shopping_cart(self, request, pk=None):
        return Response({'status': 'Выполнился экшн корзины'})
    
    
class TagViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    
    
class IngredientViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    