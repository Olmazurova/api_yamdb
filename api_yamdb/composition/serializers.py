from rest_framework import serializers, status
from rest_framework.relations import SlugRelatedField

from composition.models import Category, Titles, Reviews, Genres, Comment, User


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        fields = '__all__'
        model = Category


class TitlesSerializer(serializers.ModelSerializer):
    """Сериализатор произведений."""
    category = serializers.SlugRelatedField(
        read_only=True, slug_field='slug'
    )
    # genre = 

    class Meta:
        fields = '__all__'
        model = Titles


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор рецензий."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
    )

    class Meta:
        fields = '__all__'
        model = Reviews


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:

        fields = ('name', 'slug')
        model = Genres


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев."""
    reviews = serializers.StringRelatedField(
        read_only=True,
    )
    author = serializers.StringRelatedField(
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = Comment
