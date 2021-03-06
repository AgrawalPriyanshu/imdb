from django.contrib.auth import login as django_login, logout as django_logout
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        django_login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=200)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        user = request.user
        django_logout(request)
        try:
            token = Token.objects.get(user=user)
            token.delete()
            return Response(status=204)
        except Exception as e:
            return Response({"msg": "User not logged in "}, status=status.HTTP_204_NO_CONTENT, headers=None)
