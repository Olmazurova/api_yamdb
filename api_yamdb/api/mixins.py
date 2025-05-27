from rest_framework import serializers


class AuthorFieldMixin(serializers.ModelSerializer):
    """Миксин настраивает поле автора."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
