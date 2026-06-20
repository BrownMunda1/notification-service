from django.http import HttpResponseNotAllowed

from rest_framework.request import Request
from rest_framework import status, generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response

from users.serializers import UserSerializer

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer
