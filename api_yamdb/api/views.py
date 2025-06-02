from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS

from users.permissions import (
    IsAdmin, IsAuthorOrAdminOrModerator,
    IsAdminOrReadOnly, IsOwnerOrReadOnly
)

from api.serializers import (
    GroupSerializer, TitleReadSerializer,
    ReviewSerializer, CommentSerializer,
    GenreSerializer, TitleCreateSerializer
)
from reviews.models import Comment, Genre, Group, Review, Title


class GroupViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet модели Group."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Group, slug=slug)


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet модели Title."""
    queryset = Title.objects.all()
    # serializer_class = TitleReadSerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (filters.SearchFilter,)
    # search_fields = ('name', 'year', 'group__slug', 'genre__slug')

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet модели Review."""

    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthorOrAdminOrModerator]
    permission_classes = (IsOwnerOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

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


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet модели Comment."""
    
    serializer_class = CommentSerializer
    # permission_classes = [IsAuthorOrAdminOrModerator]
    permission_classes = (IsOwnerOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

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
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Genre, slug=slug)
