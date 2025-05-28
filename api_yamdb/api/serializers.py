from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.relations import SlugRelatedField

from reviews.constants import MAX_SCORE, MIN_SCORE
from reviews.models import Comment, Genre, Group, Title, Review
from .mixins import AuthorFieldMixin

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        fields = '__all__'
        model = Group


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведений."""

    group = serializers.SlugRelatedField(
        read_only=True, slug_field='slug'
    )
    raiting = serializers.SerializerMethodField()
    # genre =

    class Meta:
        fields = '__all__'
        model = Title

    def get_raiting(self, obj):
        title = self.context.get('titles_id')
        return Review.objects.filter(title=title).annotate()


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

class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CommentSerializer(AuthorFieldMixin, serializers.ModelSerializer):
    """Сериализатор комментариев."""

    review = serializers.StringRelatedField(
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
