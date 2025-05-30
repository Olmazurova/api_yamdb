from django.contrib.auth import get_user_model
from django.db.models import Avg, IntegerField
from rest_framework import serializers, status
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueTogetherValidator


from reviews.constants import MAX_SCORE, MIN_SCORE
from reviews.models import Comment, Genre, Group, Title, Review
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

    rating = serializers.SerializerMethodField()
    category = GroupSerializer(read_only=True, source='group')
    genre = GenreSerializer(read_only=True, many=True)


    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        model = Title

    def get_rating(self, obj):
        title = obj.id
        result = Review.objects.filter(title=title).aggregate(
            rating=Avg('score', output_field=IntegerField())
        )
        return result.get('rating')


class ReviewSerializer(AuthorFieldMixin, serializers.ModelSerializer):
    """Сериализатор рецензий."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        default=CurrentUserDefault(),
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value):
        if value not in range(MIN_SCORE, MAX_SCORE + 1):
            raise serializers.ValidationError('Оценка должна быть от 1 до 10.')
        return value

    def validate(self, attrs):
        title = self.context.get('view').kwargs.get('title_id')
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
