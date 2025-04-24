# api/views.py

from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes
from api.permissions import IsCustomer, IsVendor, IsAdminUser
from rest_framework import status
from django.contrib.auth import get_user_model
from api.serializers import UserSerializer



from api.models import (
    Address, Order, Transaction, Wallet,
    Inventory, Discount, Item, UsedItem,
    User, Cart, Bid, OrderItem, Notification, Rating
)

from api.filters import (
    CartFilters,
    ItemFilters, 
    RatingFilter,
    OrderFilters,
    DiscountFilter, 
    OrderItemFilter, 
    NotificationFilter, 
    UsedItemFilters
)
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers import (
    AddressSerializer, OrderSerializer, TransactionSerializer, WalletSerializer,
    InventorySerializer, DiscountSerializer, ItemSerializer,
    UserSerializer, CartSerializer, BidSerializer, OrderItemSerializer, 
    CustomerSerializer, NotificationSerializer, RatingSerializer, UsedItemSerializer, 
    CartCreateSerializer, CreateOrderItemSerializer, UserUpdateSerializer, AddressUpdateSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    # get the user and its address
    user = request.user
    user_serializer = UserSerializer(user)
    addresses = user.user_address.all()
    # print(addresses) # user_address = related_name from Address model
    address_serializer = AddressSerializer(addresses, many=True)

    return Response({
        'user': user_serializer.data,
        'addresses': address_serializer.data
    })

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer 
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return User.objects.all()
        return User.objects.filter(id=user.id)  # Users can only see their own profile

    def perform_update(self, serializer):
        # Any additional logic before saving
        serializer.save()


class AddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return AddressUpdateSerializer
        return AddressSerializer  
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return Address.objects.all()
        return Address.objects.filter(user=user)  # Users can only see their own addresses

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        

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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemFilters
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'admin':
            return Item.objects.all()
        elif user.user_type == 'customer':
            return Item.objects.all()
        return Item.objects.filter(vendor=user)


class UsedItemViewSet(ModelViewSet):
    queryset = UsedItem.objects.all()
    serializer_class = UsedItemSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UsedItemFilters
    

    def perform_create(self, serializer):
        # Automatically set the user to the current user
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Automatically set the user to the current user
        serializer.save(user=self.request.user)
        
    def perform_destroy(self, instance):
        # Automatically set the user to the current user
        instance.delete()
   

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilters
    
    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        
        if user.user_type == 'admin':
            return Order.objects.all()
        return Order.objects.filter(user=user)


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
        
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateOrderItemSerializer
        return OrderItemSerializer
    
class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [JWTAuthentication]


class DiscountViewSet(ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated]
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
    
     
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CartCreateSerializer
        return CartSerializer
    
    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        
        if user.user_type == 'admin':
            return Cart.objects.all()
        return Cart.objects.filter(user=user)  
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class BidViewSet(ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        item_id = self.request.query_params.get('item_id', None)

        if user.user_type == 'admin':
            if item_id:
                return Bid.objects.filter(used_item=item_id)
            return Bid.objects.all()
        
        queryset = Bid.objects.all()
        if item_id:
            queryset = queryset.filter(used_item=item_id)
        return queryset


        

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
        
    
        
        
# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import hashlib
import hmac
import os
from django.contrib.auth import get_user_model

User = get_user_model()

class TelegramLoginView(APIView):
    def post(self, request):
        data = request.data
        
        # 1. Verify Telegram data
        if not self.verify_telegram_data(data):
            return Response(
                {"error": "Invalid Telegram authentication"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 2. Get or create user
        user = self.get_or_create_user(data)
        
        # 3. Generate auth token (using your existing token mechanism)
        token = your_token_generation_method(user)
        
        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_type": user.user_type
            },
            "token": token
        })
    
    def verify_telegram_data(self, data):
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        
        check_string = "\n".join(
            f"{key}={data[key]}" 
            for key in sorted(data.keys()) 
            if key != "hash"
        )
        
        computed_hash = hmac.new(
            secret_key, 
            check_string.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        return computed_hash == data.get('hash')
    
    def get_or_create_user(self, data):
        # Try to find existing user by Telegram ID
        user = User.objects.filter(telegram_id=data['id']).first()
        
        if not user:
            # Create new user
            username = data.get('username') or f"tg_{data['id']}"
            user = User.objects.create(
                telegram_id=data['id'],
                username=username,
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                user_type='customer'  # Default type, adjust as needed
            )
        
        return user
    

User = get_user_model()
class RegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Set default values
            serializer.validated_data['verification_status'] = 'verified'
            
            # Handle vendor-specific fields
            if serializer.validated_data.get('user_type') == 'vendor':
                serializer.validated_data['vendor_type'] = 'individual'
            else:
                serializer.validated_data['vendor_type'] = None
                serializer.validated_data['business_name'] = ''
                serializer.validated_data['business_license'] = ''
            
            user = serializer.save()
            
            return Response({
                "message": "Registration successful. You can now login.",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# api/views.py
class TelegramRegisterView(APIView):
    def post(self, request):
        data = request.data
        
        # Verify required fields
        if not data.get('telegram_id'):
            return Response(
                {"error": "Telegram ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate a unique username if not provided
        username = data.get('username', f"tg_{data['telegram_id']}")
        
        # Create user data
        user_data = {
            'telegram_id': data['telegram_id'],
            'username': username,
            'email': data.get('email', f"{data['telegram_id']}@telegram.temp"),
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'password': make_password(str(uuid.uuid4())),  # Random password
            'user_type': data.get('user_type', 'customer'),
            'vendor_type': data.get('vendor_type'),
            'business_name': data.get('business_name', ''),
            'verification_status': 'verified',
            'phone': data.get('phone', '')
        }
        
        serializer = UserSerializer(data=user_data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)