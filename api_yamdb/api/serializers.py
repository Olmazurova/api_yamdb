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
        return value in range(MIN_SCORE, MAX_SCORE + 1)


class CommentSerializer(AuthorFieldMixin, serializers.ModelSerializer):
    """Сериализатор модели Comment."""

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
