from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets

from api.serializers import (
    GroupSerializer, TitleSerializer, ReviewSerializer,
    GenreSerializer, CommentSerializer
)
from reviews.models import Group, Title, Review, Genre, Comment, User


class GroupViewSet(viewsets.ModelViewSet):
    """ViewSet модели Group."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    # permission_classes = 


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet модели Title."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    # permission_classes = 


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet модели Review."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # permission_classes = 

    def get_title_id(self):
        title_id = self.kwargs.get("title_id")

        return title_id

    def get_queryset(self):

        return Review.objects.filter(
            title_id=self.get_title_id()
        )

class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet модели Comment."""
    
    serializer_class = CommentSerializer
    # permission_classes =

    def get_review_id(self):
        review_id = self.kwargs.get("review_id")

        return review_id

    def get_queryset(self):

        return Comment.objects.filter(
            review_id=self.get_review_id()
        )


class GenreViewSet(viewsets.ModelViewSet):
    """ViewSet модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    # permission_classes =

