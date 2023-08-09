from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (Cart, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User

from .filters import IngredientFilter, TagFilter
from .mixins import CreateRetrieveViewSet, UpdateDeleteViewSet
from .pagination import CustomPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .serializers import (IngredientSerializer, PreviewRecipeSerializer,
                          RecipeSerializer, SubscriptionSerializer,
                          TagSerializer, UserSerializer)


class UserViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = UserSerializer
    add_serializer = SubscriptionSerializer
    queryset = User.objects.all()
    pagination_class = CustomPageNumberPagination
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['get', ],
            permission_classes=(IsAuthenticated,)
            )
    def subscriptions(self, request):
        print(request.data)
        user = request.user
        pages = self.paginate_queryset(
            User.objects.filter(subscribefor__user=user)
        )
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get', ],
            permission_classes=(IsAuthenticated,)
            )
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get', ],
            permission_classes=(IsAuthenticated,)
            )
    def set_password(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        user.set_password(request.data['new_password'])
        user.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', ],
            permission_classes=(IsAuthenticated,)
            )
    def subscribe(self, request, pk=None):
        pass

    @subscribe.mapping.post
    def subscribe_for(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        subscription, created = Subscription.objects.get_or_create(
            user_id=request.user.id,
            author_id=int(pk)
        )
        if author and created:
            serializer = UserSerializer(author, context={'request': request})
            return Response(serializer.data)
        if author and not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        subscription = Subscription.objects.filter(
            user_id=request.user.id,
            author_id=int(pk)
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = RecipeSerializer
    add_serializer = PreviewRecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    filter_class = TagFilter

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        if self.request.user.is_authenticated:
            is_favorited = self.request.query_params.get('is_favorited')
            if is_favorited:
                queryset = queryset.filter(
                    in_favorites__user=self.request.user
                )

            in_cart = self.request.query_params.get('is_in_shopping_cart')
            if in_cart:
                queryset = queryset.filter(in_cart__user=self.request.user)

            return queryset

        return queryset

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @favorite.mapping.post
    def add_to_favorites(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        Favorite.objects.create(recipe=recipe, user=user)
        serializer = PreviewRecipeSerializer(recipe)
        return Response(serializer.data)

    @favorite.mapping.delete
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
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @shopping_cart.mapping.post
    def add_to_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        Cart.objects.create(recipe=recipe, user=user)
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

    @action(detail=False, methods=['get', ],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        in_cart = (
            IngredientAmount.objects.filter(recipe__in_cart__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount')))
        shopping_cart = [(f'{ingredient["ingredient__name"]} - '
                          f'{ingredient["amount"]}'
                          f'{ingredient["ingredient__measurement_unit"]}')
                         for ingredient in in_cart]
        shopping_cart.insert(0, 'ВАШ СПИСОК ПОКУПОК')
        if user.first_name and user.last_name:
            shopping_cart.insert(
                0,
                f'Уважаемый(-ая), {user.first_name} {user.last_name}!'
            )
        else:
            shopping_cart.insert(
                0,
                f'Уважаемый(-ая), {user.username} {user.last_name}!'
            )

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        pdfmetrics.registerFont(
            TTFont(
                'DejaVu',
                'static/DejaVuSansCondensed.ttf',
                'UTF-8'
            )
        )
        page = canvas.Canvas(response)
        page.setFont('DejaVu', size=16)
        page.drawString(170, 800, shopping_cart[0])
        page.drawString(220, 770, shopping_cart[1])
        height = 730
        for row in shopping_cart[2:]:
            page.drawString(75, height, row)
            height -= 25
        page.showPage()
        page.save()
        return response


class TagViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(CreateRetrieveViewSet, UpdateDeleteViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (IngredientFilter, )
    search_fields = ('^name',)
