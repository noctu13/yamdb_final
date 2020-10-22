from django_filters import rest_framework as filters

from api.models import Title


class TitleFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="contains")
    year = filters.CharFilter(field_name="year")
    genre = filters.CharFilter(field_name="genre__slug")
    category = filters.CharFilter(field_name="category__slug")

    class Meta:
        model = Title
        fields = ["name", "genre", "category", "year"]
