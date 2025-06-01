from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault


class AuthorFieldMixin(serializers.ModelSerializer):
    """Миксин настраивает поле автора в сериализаторе."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True, default=CurrentUserDefault(),
    )
