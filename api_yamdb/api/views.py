import re
import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .constants import MAX_LENGTH_EMAIL, MAX_LENGTH_NAME
from api.serializers import (CommentSerializer, GenreSerializer,
                             GroupSerializer, ReviewSerializer,
                             TitleCreateSerializer, TitleReadSerializer,
                             TokenObtainSerializer, UserProfileSerializer,
                             UserRegistrationSerializer, UserSerializer)
from reviews.models import Comment, Genre, Group, Review, Title
from .filters import TitleFilter
from .mixins import (AdminPermissionMixin, AuthorPermissionMixin,
                     HTTPMethodsMixin, SlugSearchFilterMixin)
from users.models import User
from .permissions import IsAdmin


class GroupViewSet(
    AdminPermissionMixin,
    SlugSearchFilterMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet модели Group."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TitleViewSet(
    AdminPermissionMixin, HTTPMethodsMixin, viewsets.ModelViewSet
):
    """ViewSet модели Title."""

    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleCreateSerializer


class ReviewViewSet(
    AuthorPermissionMixin, HTTPMethodsMixin, viewsets.ModelViewSet
):
    """ViewSet модели Review."""

    serializer_class = ReviewSerializer

    def get_title_id(self):
        title_id = self.kwargs.get('title_id')
        return title_id

    def get_queryset(self):
        return Review.objects.filter(
            title_id=self.get_title_id()
        )

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.get_title_id())
        return serializer.save(author=self.request.user, title=title)


class CommentViewSet(
    AuthorPermissionMixin, HTTPMethodsMixin, viewsets.ModelViewSet
):
    """ViewSet модели Comment."""

    serializer_class = CommentSerializer

    def get_review_id(self):
        review_id = self.kwargs.get('review_id')
        return review_id

    def get_queryset(self):
        return Comment.objects.filter(
            review_id=self.get_review_id()
        )

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.get_review_id())
        return serializer.save(author=self.request.user, review=review)


class GenreViewSet(
    AdminPermissionMixin,
    SlugSearchFilterMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Genre, slug=slug)


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
    """Получение JWT-токена на основе username и confirmation_code."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'token': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username
            },
            status=status.HTTP_200_OK
        )
