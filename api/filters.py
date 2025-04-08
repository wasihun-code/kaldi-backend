import django_filters
from api.models import (Order, OrderItem)

class OrderItemFilter(django_filters.FilterSet):
    """Filter by order status"""
    status = django_filters.CharFilter(
        field_name='order__status',
        lookup_expr='iexact',
    )

    class Meta:
        model = OrderItem
        fields = []
