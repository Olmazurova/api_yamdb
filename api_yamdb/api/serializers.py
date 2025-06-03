import re

from django.contrib.auth import get_user_model
from django.db.models import Avg, IntegerField
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from reviews.constants import (MAX_SCORE, MIN_SCORE,
                               MAX_LENGTH_EMAIL, MAX_LENGTH_NAME)
from reviews.models import Comment, Genre, Group, Title, Review
from .mixins import AuthorFieldMixin

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        exclude = ('id',)
        model = Group


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:
        exclude = ('id',)
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор произведений для чтения."""

    rating = serializers.ReadOnlyField()
    category = GroupSerializer(
        read_only=True,
        source='group',
    )
    genre = GenreSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        model = Title


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор произведений для записи."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        source='group',
        queryset=Group.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )


class ReviewSerializer(AuthorFieldMixin, serializers.ModelSerializer):
    """Сериализатор рецензий."""

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value):
        if value not in range(MIN_SCORE, MAX_SCORE + 1):
            raise serializers.ValidationError('Оценка должна быть от 1 до 10.')
        return value

    def validate(self, attrs):
        title = self.context.get('view').kwargs.get('title_id')
        if self.instance:
            return attrs
        if Review.objects.filter(
                title=title, author=CurrentUserDefault()(serializer_field=self)
        ).exists():
            raise serializers.ValidationError(
                'Пользователь может оставить только один отзыв к произведению!'
            )
        return attrs


class CommentSerializer(AuthorFieldMixin, serializers.ModelSerializer):
    """Сериализатор комментариев."""

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserRegistrationSerializer(serializers.Serializer):
    """
    Сериализатор для регистрации пользователя.
    Проверяет уникальность email и username, а также запрещает username 'me'.
    """

    email = serializers.EmailField(max_length=MAX_LENGTH_EMAIL)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=MAX_LENGTH_NAME
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя "me" недопустимо в качестве username.'
            )
        return value

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')

        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()

        if user_by_email and user_by_username:
            if user_by_email != user_by_username:
                raise serializers.ValidationError(
                    'Пользователь с таким username и email уже существует, '
                    'но принадлежат разным аккаунтам.'
                )
        elif user_by_email:
            raise serializers.ValidationError('Этот email уже используется.')
        elif user_by_username:
            raise serializers.ValidationError(
                'Этот username уже используется.'
            )

        return attrs


class TokenObtainSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена
    с использованием username и confirmation_code.
    """
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])

        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения'}
            )

        data['user'] = user  # Добавляем user в validated_data
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для полной информации о пользователе."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля пользователя,
    с полями username, email и ролью в режиме только для чтения.
    """

    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)

    def validate_email(self, value):
        if len(value) > MAX_LENGTH_EMAIL:
            raise serializers.ValidationError("Email слишком длинный")
        return value

    def validate_username(self, value):
        if len(value) > MAX_LENGTH_NAME:
            raise serializers.ValidationError("Username слишком длинный")
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                "Недопустимые символы в username"
            )
        return value
