from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.filters import SearchFilter

from users.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly


class AuthorFieldMixin(serializers.ModelSerializer):
    """Миксин настраивает поле автора в сериализаторе."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True, default=CurrentUserDefault(),
    )


class AdminPermissionMixin:
    """Миксин добавляет класс разрешения уровня администратора."""

    permission_classes = (IsAdminOrReadOnly,)


class OwnerPermissionMixin:
    """Миксин добавляет класс разрешения для авторов отзывов и комментариев."""

    permission_classes = (IsOwnerOrReadOnly,)


class HTTPMethodsMixin:
    """Миксин определяет http методы, которые будет обрабатывать вьюсет."""

    http_method_names = ['get', 'post', 'patch', 'delete']


class SlugSearchFilterMixin:
    """Миксин добавляет класс фильтрации SearchFilter."""

    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
