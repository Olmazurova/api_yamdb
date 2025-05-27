from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews.models import (Category, Comment, Genre, MAX_SCORE, MIN_SCORE,
                            Title, Review)
from .mixins import AuthorFieldMixin

User = get_user_model()


class ReviewSerializer(AuthorFieldMixin, serializers.ModelSerializer):
    """Сериализатор модели Review."""

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
    """Сериализатор модели Comment."""

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
