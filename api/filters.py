import django_filters
from api.models import (Item, OrderItem)

class OrderItemFilter(django_filters.FilterSet):
    """Filter by order status"""
    status = django_filters.CharFilter(
        field_name='order__status',
        lookup_expr='iexact',
    )

    class Meta:
        model = OrderItem
        fields = []


class ItemFilters(django_filters.FilterSet):
    """ Filter Items by price, in_stock(from inventory) and locations(from inventory) """
    in_stock = django_filters.BooleanFilter(
        field_name='inventory__in_stock',
    )
    min_price = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='gte',
        label='Minimum Price'
    )
    max_price = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='lte',
        label='Maximum Price'
    )
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Name'
    )
    location = django_filters.CharFilter(
        field_name='inventory__location',
        lookup_expr='icontains',
        label='Location'
    )
    
    class Meta:
        model = Item
        fields = {
            'price': ['exact', 'lt', 'gt']
        }