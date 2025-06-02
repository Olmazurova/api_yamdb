from django_filters import rest_framework as filters
from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """Собственный фильтр для TitleViewSet."""

    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='exact'
    )
    category = filters.CharFilter(
        field_name='group__slug',
        lookup_expr='exact'
    )
    year = filters.NumberFilter(
        field_name='year',
        lookup_expr='exact'
    )
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='exact'
    )

    class Meta:
        model = Title
        fields = ('genre', 'category', 'year', 'name')
