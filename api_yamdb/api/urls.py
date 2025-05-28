from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    GroupViewSet, TitleViewSet, ReviewViewSet,
    CommentViewSet, GenreViewSet
)

router_v1 = DefaultRouter()
router_v1.register('categories', GroupViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('titles', TitleViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
