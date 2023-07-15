from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .mixins import *
from users.models import User

class UserViewSet(CreateRetrieveViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    