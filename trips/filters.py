import django_filters
from .models import Trip


class TripFilter(django_filters.FilterSet):
    cat = django_filters.NumberFilter(field_name='cat__id', label='ID кота')
    status = django_filters.ChoiceFilter(choices=Trip.status.field.choices)
    title = django_filters.CharFilter(lookup_expr='icontains', label='Поиск по названию')

    class Meta:
        model = Trip
        fields = ['cat', 'status', 'title']
