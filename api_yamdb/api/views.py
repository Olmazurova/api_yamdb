import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.mixins import (AdminPermissionMixin, AuthorPermissionMixin,
                        GenreGroupMixin, HTTPMethodsMixin)
from api.permissions import IsAdmin
from api.serializers import (CommentSerializer, GenreSerializer,
                             GroupSerializer, ReviewSerializer,
                             TitleCreateSerializer, TitleReadSerializer,
                             TokenObtainSerializer, UserProfileSerializer,
                             UserRegistrationSerializer, UserSerializer)
from reviews.models import Comment, Genre, Group, Review, Title
from users.models import User


class GroupViewSet(GenreGroupMixin):
    """ViewSet модели Group."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TitleViewSet(
    AdminPermissionMixin, HTTPMethodsMixin, viewsets.ModelViewSet
):
    """ViewSet модели Title."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('-id')
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
        return self.kwargs.get('title_id')

    def get_queryset(self):
        return Review.objects.filter(
            title_id=self.get_title_id()
        )

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.get_title_id())
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(
    AuthorPermissionMixin, HTTPMethodsMixin, viewsets.ModelViewSet
):
    """ViewSet модели Comment."""

    serializer_class = CommentSerializer

    def get_review_id(self):
        return self.kwargs.get('review_id')

    def get_queryset(self):
        return Comment.objects.filter(
            review_id=self.get_review_id()
        )

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.get_review_id())
        serializer.save(author=self.request.user, review=review)


class GenreViewSet(GenreGroupMixin):
    """ViewSet модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с пользователями.
    Позволяет искать пользователей по username и предоставляет
    эндпоинт 'me' для работы с собственным профилем пользователя.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    @action(
        detail=False,
        methods=['get', 'patch',],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
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
