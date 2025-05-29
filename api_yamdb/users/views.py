import re
import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsAdmin
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    TokenObtainSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с пользователями.
    Позволяет искать пользователей по username и предоставляет
    эндпоинт 'me' для работы с собственным профилем пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action == 'me':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get', 'patch', 'delete'])
    def me(self, request):
        if request.method == 'DELETE':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        user = request.user

        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)

        serializer = UserProfileSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        email = request.data.get('email')
        if email and len(email) > 254:
            return Response(
                {'email': 'Email слишком длинный'},
                status=status.HTTP_400_BAD_REQUEST
            )

        username = request.data.get('username')
        if username:
            if len(username) > 150:
                return Response(
                    {'username': 'Username слишком длинный'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not re.match(r'^[\w.@+-]+\Z', username):
                return Response(
                    {'username': 'Недопустимые символы в username'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer.save()
        return Response(serializer.data)


class SignupView(APIView):
    """
    Регистрация пользователя.
    Создаёт пользователя и отправляет код подтверждения на email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, created = User.objects.get_or_create(
            username=serializer.validated_data['username'],
            defaults={
                'email': serializer.validated_data['email'],
                'confirmation_code': secrets.token_urlsafe(32)
            }
        )
        if not created:
            user.confirmation_code = secrets.token_urlsafe(32)
            user.save()

        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код подтверждения: {user.confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {'email': user.email, 'username': user.username},
            status=status.HTTP_200_OK
        )


class TokenView(APIView):
    """
    Получение JWT-токена на основе username и confirmation_code.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, username=serializer.validated_data['username'])

        if user.confirmation_code != serializer.validated_data['confirmation_code']:
            return Response(
                {'error': 'Неверный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)
        return Response({'token': str(refresh.access_token)}, status=status.HTTP_200_OK)