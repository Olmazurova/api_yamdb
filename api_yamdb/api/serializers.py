from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.relations import SlugRelatedField

from reviews.models import (Comment, Genre, Group, MAX_SCORE, MIN_SCORE,
                            Title, Review)
from .mixins import AuthorFieldMixin

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        fields = ('name', 'slug')
        model = Group

class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:

        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведений."""

    category = GroupSerializer(read_only=True, source='group')
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title


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
        title = self.context.get('request').get('titles_id')
        if Review.objects.filter(
                title=title, author=attrs.get('author')
        ).exists():
            raise serializers.ValidationError(
                'Пользователь может оставить только один отзыв к произведению!'
            )
        return attrs


class CommentSerializer(AuthorFieldMixin, serializers.ModelSerializer):
    """Сериализатор комментариев."""

    review = serializers.StringRelatedField(
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
