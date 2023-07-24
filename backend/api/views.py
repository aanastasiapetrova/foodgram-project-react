from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .serializers import *
from .mixins import *
from users.models import User
from recipes.models import *
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
import djoser.views as djoser
from .pagination import CustomPageNumberPagination
from .permissions import *
from django.db.models import Sum
from fpdf import FPDF
from rest_framework import status

class UserViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = UserSerializer
    add_serializer = SubscriptionSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    pagination_class = CustomPageNumberPagination
    
    @action(detail=False, methods=['get',], permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        pages = self.paginate_queryset(User.objects.filter(subscribefor__user=user))
        serializer = SubscriptionSerializer(pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get',], permission_classes=(IsAuthenticated,))
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
        
    @action(detail=False, methods=['get',], permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        user.set_password(request.data['new_password'])
        user.save()
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk=None):
        pass
    
    @subscribe.mapping.post
    def subscribe_for(self, request, pk=None):
        user = get_object_or_404(User, pk=request.user.id)
        author = get_object_or_404(User, pk=pk)
        subscription = Subscription.objects.get(user_id=user.pk, author_id=int(pk))
        if author and not subscription:
            subscription = Subscription.objects.create(user_id=user.pk, author_id=int(pk))
            serializer = UserSerializer(author, context={'request': request})
            return Response(serializer.data)
        if author and subscription:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        user = get_object_or_404(User, pk=request.user.id)
        author = get_object_or_404(User, pk=pk)
        subscription = Subscription.objects.filter(user_id=user.pk, author_id=int(pk))
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

class RecipeViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = RecipeSerializer
    add_serializer = PreviewRecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    
    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorites(self, request, pk=None):
        pass
    
    @favorites.mapping.post
    def add_to_favorites(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        favorite = Favorite.objects.create(recipe=recipe, user=user)
        serializer = PreviewRecipeSerializer(recipe)
        return Response(serializer.data)
    
    @favorites.mapping.delete
    def delete_from_favorites(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        favorite = Favorite.objects.filter(recipe=recipe, user=user)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        pass
    
    @shopping_cart.mapping.post
    def add_to_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        cart = Cart.objects.create(recipe=recipe, user=user)
        serializer = PreviewRecipeSerializer(recipe)
        return Response(serializer.data)
    
    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        cart = Cart.objects.filter(recipe=recipe, user=user)
        if cart.exists():
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get',])
    def download_shopping_cart(self, request):
        user = request.user
        in_cart = (IngredientAmount.objects.filter(recipe__in_cart__user=request.user)
                   .values('ingredient__name', 'ingredient__measurement_unit')
                   .annotate(amount=Sum('amount')))
        shopping_cart = [f'{ingredient["ingredient__name"]} - {ingredient["amount"]} {ingredient["ingredient__measurement_unit"]}'
                         for ingredient in in_cart]
        shopping_cart.insert(0,'ВАШ СПИСОК ПОКУПОК')
        if user.first_name and user.last_name:
            shopping_cart.insert(0, f'Уважаемый(-ая), {user.first_name} {user.last_name}!')
        else:
            shopping_cart.insert(0, f'Уважаемый(-ая), {user.username} {user.last_name}!')
        
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'static/DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', size=10)
        pdf.cell(pdf.w-20, 10, shopping_cart[0], border=0, align='C', fill=0)
        pdf.ln(6)
        pdf.cell(pdf.w-20, 10, shopping_cart[1], border=0, align='C', fill=0)
        pdf.ln(10)
        for row in shopping_cart[2:]:
            pdf.cell(pdf.w, 10, row, border=0, align='L', fill=0)
            pdf.ln(6)
        pdf.output(f'static/shopping_list.pdf')
        return Response()
        
    
class TagViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    
    
class IngredientViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    