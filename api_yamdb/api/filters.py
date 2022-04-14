from django_filters import CharFilter, FilterSet, AllValuesFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='contains')
    genre = AllValuesFilter(field_name='genre__slug')
    category = AllValuesFilter(field_name='category__slug')

    class Meta:
        model = Title
        fields = ('name', 'year', 'genre', 'category')
