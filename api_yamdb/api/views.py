from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS

from api.filters import TitleFilter
from api.mixins import (AdminPermissionMixin, AuthorPermissionMixin,
                        GenreGroupMixin, HTTPMethodsMixin)
from api.serializers import (CommentSerializer, GenreSerializer,
                             GroupSerializer, ReviewSerializer,
                             TitleCreateSerializer, TitleReadSerializer)
from reviews.models import Comment, Genre, Group, Review, Title


class GroupViewSet(GenreGroupMixin):
    """ViewSet модели Group."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TitleViewSet(
    AdminPermissionMixin, HTTPMethodsMixin, viewsets.ModelViewSet
):
    """ViewSet модели Title."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('-id')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleCreateSerializer


class ReviewViewSet(
    AuthorPermissionMixin, HTTPMethodsMixin, viewsets.ModelViewSet
):
    """ViewSet модели Review."""

    serializer_class = ReviewSerializer

    def get_title_id(self):
        return self.kwargs.get('title_id')

    def get_queryset(self):
        return Review.objects.filter(
            title_id=self.get_title_id()
        )

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.get_title_id())
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(
    AuthorPermissionMixin, HTTPMethodsMixin, viewsets.ModelViewSet
):
    """ViewSet модели Comment."""

    serializer_class = CommentSerializer

    def get_review_id(self):
        return self.kwargs.get('review_id')

    def get_queryset(self):
        return Comment.objects.filter(
            review_id=self.get_review_id()
        )

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.get_review_id())
        serializer.save(author=self.request.user, review=review)


class GenreViewSet(GenreGroupMixin):
    """ViewSet модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
