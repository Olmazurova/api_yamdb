from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from api.mixins import AuthorFieldMixin
from reviews.constants import MAX_SCORE, MIN_SCORE
from reviews.models import Comment, Genre, Group, Review, Title

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
