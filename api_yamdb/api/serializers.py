from rest_framework import serializers, status
from rest_framework.relations import SlugRelatedField

from reviews.models import Group, Title, Review, Genre, Comment, User


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
    # genre = 

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор рецензий."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
    )

    class Meta:
        fields = '__all__'
        model = Review


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:

        fields = ('name', 'slug')
        model = Genre


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев."""
    review = serializers.StringRelatedField(
        read_only=True,
    )
    author = serializers.StringRelatedField(
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = Comment
