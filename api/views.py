# api/views.py

from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes
from api.permissions import IsCustomer, IsVendor, IsAdminUser


from api.models import (
    Address, Order, Transaction, Wallet,
    Inventory, Discount, Item,
    User, Cart, Bid, OrderItem, Notification, Rating
)

from api.filters import (
    CartFilters,
    ItemFilters, 
    RatingFilter,
    DiscountFilter, 
    OrderItemFilter, 
    NotificationFilter, 
)
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers import (
    AddressSerializer, OrderSerializer, TransactionSerializer, WalletSerializer,
    InventorySerializer, DiscountSerializer, ItemSerializer,
    UserSerializer, CartSerializer, BidSerializer, OrderItemSerializer, 
    CustomerSerializer, NotificationSerializer, RatingSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class AddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class WalletViewSet(ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter
    
    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        if user.user_type == 'admin':
            return Notification.objects.all()
        else:
            return Notification.objects.filter(user=user)


class InventoryViewSet(ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [JWTAuthentication]



class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemFilters
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'admin':
            return Item.objects.all()
        return Item.objects.filter(vendor=user)


   
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderItemFilter
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return OrderItem.objects.all()
        elif user.user_type == 'vendor':
            # Vendors can see order items for their own items
            return OrderItem.objects.filter(item__vendor=user).select_related('order', 'item', 'order__user')
        else:
            # Customers can only see their own order items
            return OrderItem.objects.filter(order__user=user)
    
class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [JWTAuthentication]


class DiscountViewSet(ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DiscountFilter
    
    
    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        
        if user.user_type == 'admin':
            return Discount.objects.all()
        return Discount.objects.filter(vendor=user)


class RatingViewSet(ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RatingFilter
    
    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        
        if user.user_type == 'admin':
            return Rating.objects.all()
        return Rating.objects.filter(item__vendor=user)


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CartFilters
    
    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        
        if user.user_type == 'admin':
            return Cart.objects.all()
        return Cart.objects.filter(user=user)  


class BidViewSet(ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    authentication_classes = [JWTAuthentication]


class VendorCustomerViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'vendor':
            
            order_customers = User.objects.filter(
                orders__order_items__item__vendor=user
            ).distinct()
            
            return order_customers.filter(user_type='customer').distinct()
        
        # if the user is admin, return all customers
        return User.objects.filter(user_type='customer').distinct()
        
    
        
        