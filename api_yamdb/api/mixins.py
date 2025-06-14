from rest_framework import mixins, serializers, viewsets
from rest_framework.fields import CurrentUserDefault
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny

from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly


class AuthorFieldMixin(serializers.ModelSerializer):
    """Миксин настраивает поле автора в сериализаторе."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True, default=CurrentUserDefault(),
    )


class AdminPermissionMixin:
    """Миксин добавляет класс разрешения уровня администратора."""

    permission_classes = (IsAdminOrReadOnly,)


class AuthorPermissionMixin:
    """Миксин добавляет класс разрешения для авторов отзывов и комментариев."""

    permission_classes = (IsAuthorOrReadOnly,)


class AllowAnyPermissionMixin:
    """Миксин добавляет класс разрешения для всех."""

    permission_classes = (AllowAny,)


class HTTPMethodsMixin:
    """Миксин определяет http методы, которые будет обрабатывать вьюсет."""

    http_method_names = ['get', 'post', 'patch', 'delete']


class SlugSearchFilterMixin:
    """Миксин добавляет класс фильтрации SearchFilter."""

    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreGroupMixin(
    AdminPermissionMixin,
    SlugSearchFilterMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass
