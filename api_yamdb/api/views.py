from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers import (
    GroupSerializer, TitleReadSerializer,
    ReviewSerializer, CommentSerializer,
    GenreSerializer, TitleCreateSerializer
)
from reviews.models import Comment, Genre, Group, Review, Title
from .filters import TitleFilter
from .mixins import (
    AdminPermissionMixin, OwnerPermissionMixin,
    HTTPMethodsMixin, SlugSearchFilterMixin
)


class GroupViewSet(
    AdminPermissionMixin,
    SlugSearchFilterMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet модели Group."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TitleViewSet(
    AdminPermissionMixin, HTTPMethodsMixin, viewsets.ModelViewSet
):
    """ViewSet модели Title."""

    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleCreateSerializer


class ReviewViewSet(
    OwnerPermissionMixin, HTTPMethodsMixin, viewsets.ModelViewSet
):
    """ViewSet модели Review."""

    serializer_class = ReviewSerializer

    def get_title_id(self):
        title_id = self.kwargs.get('title_id')
        return title_id

    def get_queryset(self):
        return Review.objects.filter(
            title_id=self.get_title_id()
        )

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.get_title_id())
        return serializer.save(author=self.request.user, title=title)


class CommentViewSet(
    OwnerPermissionMixin, HTTPMethodsMixin, viewsets.ModelViewSet
):
    """ViewSet модели Comment."""

    serializer_class = CommentSerializer

    def get_review_id(self):
        review_id = self.kwargs.get('review_id')
        return review_id

    def get_queryset(self):
        return Comment.objects.filter(
            review_id=self.get_review_id()
        )

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.get_review_id())
        return serializer.save(author=self.request.user, review=review)


class GenreViewSet(
    AdminPermissionMixin,
    SlugSearchFilterMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Genre, slug=slug)
