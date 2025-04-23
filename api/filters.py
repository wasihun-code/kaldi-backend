import django_filters
from api.models import (
    Cart,
    Item, 
    Order,
    Rating,
    Discount,
    OrderItem,
    Notification, 
)
from django.db.models import Q, F, Sum
import datetime
from django.utils import timezone

class OrderItemFilter(django_filters.FilterSet):
    """Filter by order status"""
    status = django_filters.CharFilter(
        field_name='order__status',
        lookup_expr='iexact',
    )

    class Meta:
        model = OrderItem
        fields = []
        

class NotificationFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(
        field_name='type',
        lookup_expr='iexact',
        label='Type'
    )
    read = django_filters.BooleanFilter(
        field_name='read',
    )
    
    class Meta:
        model = Notification
        fields = []



class DiscountFilter(django_filters.FilterSet):
    min_percentage = django_filters.NumberFilter(
        field_name='percentage',
        lookup_expr='gte',
        label='Min Percentage'
    )
    
    max_percentage = django_filters.NumberFilter(
        field_name='percentage',
        lookup_expr='lte',
        label='Max Percentage'
    )
    
    search = django_filters.CharFilter(
        method='filter_by_search',
        label='Search'
    )
    
    redemptions = django_filters.NumberFilter(
        field_name='redemptions',
        lookup_expr='gte',
        label='Min Redemptions'
    )
    
    max_redemptions = django_filters.NumberFilter(
        field_name='max_redemptions',
        lookup_expr='lte',
        label='Max Redemptions'
    )
    
    status = django_filters.CharFilter(
        method='filter_by_status',
        label='Status'
    )
        
    def filter_by_status(self, queryset, name, value):
        """
        Filters discounts by status (active/inactive).
        Active discounts:
        - Have not passed their expiry date
        - Have redemptions less than max_redemptions (if max_redemptions is set)
        """
        if value.lower() == 'active':
            queryset = queryset.filter(
                expires_at__gte=datetime.datetime.now()
            )
            # Only apply max_redemptions filter if max_redemptions is not None
            queryset = queryset.filter(
                Q(max_redemptions__isnull=True) |  # No limit on redemptions
                Q(redemptions__lt=F('max_redemptions')) 
            )# Under redemption limit
        elif value.lower() == 'inactive':
            queryset = queryset.filter(
                Q(expires_at__lt=datetime.datetime.now()) |  # Past expiry date
                Q(redemptions__gte=F('max_redemptions'), 
                max_redemptions__isnull=False)  # Reached redemption limit
            )
        return queryset

        
    
    def filter_by_search(self, queryset, name, value):
        return queryset.filter(
            Q(code__icontains=value) |
            Q(name=value)
        )
    
    class Meta:
        model = Discount
        fields = []



class RatingFilter(django_filters.FilterSet):
    min_rating = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='gte',
        label='Min rating'
    )
    
    max_rating = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='lte',
        label='Max rating'
    )
    
    # filter by item
    item = django_filters.CharFilter(
        field_name='item__name',
        lookup_expr='icontains',
        label='Item Name'
    )

    user = django_filters.NumberFilter(
        field_name='user__id',
        label='User Id'
    )

    class Meta:
        model = Rating
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
    category = django_filters.CharFilter(method='filter_search')
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(category__iexact=value)
    
    class Meta:
        model = Item
        fields = {
            'price': ['exact', 'lt', 'gt']
        }




class CartFilters(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name='item__price',
        lookup_expr='gte',
        label='Min price'
    )
    
    max_price = django_filters.NumberFilter(
        field_name='item__price',
        lookup_expr='lte',
        label='Max price'
    )
    
    # filter by item
    name = django_filters.CharFilter(
        field_name='item__name',
        lookup_expr='icontains',
        label='Item Name'
    )
    
    date = django_filters.CharFilter(
        method='filter_by_date',
        label='Date Range'
    )

    # filter by date: last3months, thisyear, lastyear, last30days
    def filter_by_date(self, queryset, name, value):
        today = timezone.now().date()

        if value == 'last15days':
            start_date = today - datetime.timedelta(days=15)
            return queryset.filter(added_at__gte=start_date)
            
        elif value == 'last3months':
            start_date = today - datetime.timedelta(days=90)
            return queryset.filter(added_at__gte=start_date)
            
        elif value == 'thisyear':
            start_date = datetime.date(today.year, 1, 1)
            return queryset.filter(added_at__gte=start_date)
            
        elif value == 'lastyear':
            start_date = datetime.date(today.year-1, 1, 1)
            end_date = datetime.date(today.year-1, 12, 31)
            return queryset.filter(added_at__range=[start_date, end_date])
            
        elif value == 'thismonth':
            start_date = datetime.date(today.year, today.month, 1)
            return queryset.filter(added_at__gte=start_date)
            
        return queryset
    
    class Meta:
        model = Cart
        fields = []
        
        

class OrderFilters(django_filters.FilterSet):
    min_total = django_filters.NumberFilter(
        method='filter_min_total',
        label='Min total'
    )
    
    max_total = django_filters.NumberFilter(
        method='filter_max_total',
        label='Max total'
    )
    
    # filter by item
    name = django_filters.CharFilter(
        field_name='order_items__item__name',
        lookup_expr='icontains',
        label='Item Name'
    )
    
    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact',
        label='Status'
    )
    
    date = django_filters.CharFilter(
        method='filter_by_date',
        label='Date Range'
    )
    
    def filter_min_total(self, queryset, name, value):
        # Annotate each order with its total, then filter
        return queryset.annotate(
            order_total=Sum(F('order_items__price_at_purchase') * F('order_items__quantity'))
        ).filter(order_total__gte=value)

    def filter_max_total(self, queryset, name, value):
        # Annotate each order with its total, then filter
        return queryset.annotate(
            order_total=Sum(F('order_items__price_at_purchase') * F('order_items__quantity'))
        ).filter(order_total__lte=value)

    def filter_by_date(self, queryset, name, value):
        today = timezone.now().date()

        if value == 'last15days':
            start_date = today - datetime.timedelta(days=15)
            return queryset.filter(created_at__gte=start_date)
            
        elif value == 'last3months':
            start_date = today - datetime.timedelta(days=90)
            return queryset.filter(created_at__gte=start_date)
            
        elif value == 'thisyear':
            start_date = datetime.date(today.year, 1, 1)
            return queryset.filter(created_at__gte=start_date)
            
        elif value == 'lastyear':
            start_date = datetime.date(today.year-1, 1, 1)
            end_date = datetime.date(today.year-1, 12, 31)
            return queryset.filter(created_at__range=[start_date, end_date])
            
        elif value == 'thismonth':
            start_date = datetime.date(today.year, today.month, 1)
            return queryset.filter(created_at__gte=start_date)
            
        return queryset
    
    class Meta:
        model = Order
        fields = []