from rest_framework.serializers import (
    ModelSerializer, SerializerMethodField
)
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from api.models import (
    Address, Transaction, Order, Wallet,
    Inventory, Discount, Item,
    Cart, Bid, User, OrderItem, Notification, Rating, UsedItem
)
from rest_framework import serializers
from django.core.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

User = get_user_model()

class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'confirm_password',
            'first_name', 'last_name', 'phone', 'user_type', 'vendor_type',
            'business_name', 'business_license', 'telegram_id', 'profile_image'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'telegram_id': {'required': False}
        }
    
    def validate(self, data):
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user



class VendorSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone', 
            'business_name', 'vendor_type', 'bussiness_license', 'profile_image'
        ]



class CustomerSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'profile_image']
        # read_only_fields = ('id')        



class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'



User = get_user_model()

class UserUpdateSerializer(ModelSerializer):
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone',
            'vendor_type', 'business_name', 'business_license',
            'telegram_id', 'profile_image'
        ]
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
            'telegram_id': {'required': False},
            'profile_image': {'required': False}
        }
    
    def validate(self, data):
        # Validate vendor-specific fields when user is a vendor
        if self.instance and self.instance.user_type == 'vendor':
            if 'business_name' in data and not data['business_name']:
                raise serializers.ValidationError("Business name is required for vendors")
            if 'vendor_type' in data and not data['vendor_type']:
                raise serializers.ValidationError("Vendor type is required for vendors")
        
        # Prevent changing user_type through update
        if 'user_type' in data and self.instance and data['user_type'] != self.instance.user_type:
            raise serializers.ValidationError("Cannot change user type after creation")
        
        return data
    
    def update(self, instance, validated_data):
        # Handle profile image separately
        profile_image = validated_data.pop('profile_image', None)
        
        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if profile_image:
            instance.profile_image = profile_image
        
        instance.save()
        return instance

class AddressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street_address', 'city', 'state', 'postal_code', 'country']
        extra_kwargs = {
            'street_address': {'required': False},
            'city': {'required': False},
            'state': {'required': False},
            'postal_code': {'required': False},
            'country': {'required': False}
        }
    
    def update(self, instance, validated_data):
        # Update address fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class WalletSerializer(ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class InventorySerializer(ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'


class ItemSerializer(ModelSerializer):
    inventory = InventorySerializer()
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'category', 'inventory', 'created_at', 'vendor', 'image']


class CreateItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'category', 'vendor']
        
    

class UsedItemSerializer(ModelSerializer):
    class Meta:
        model = UsedItem
        fields = '__all__'



class OrderItemSerializer(ModelSerializer):
    item = ItemSerializer(read_only=True)
    purchaser = SerializerMethodField()
    order = SerializerMethodField()
    
    def get_purchaser(self, obj):
        purchaser = obj.order.user

        
        return {
            'id': purchaser.id,
            'first_name': purchaser.first_name,
            'last_name': purchaser.last_name,
            'email': purchaser.email,
            'phone': purchaser.phone,
        }
        
    def get_order(self, obj):
        order = obj.order
        
        return {
            'id': order.id,
            'status': order.status,
            'created_at': order.created_at,
            'updated_at': order.updated_at,
        }
    
    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'quantity', 'price_at_purchase', 'order', 'purchaser']


class CreateOrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'price_at_purchase', 'quantity', 'order', 'item', 'image']
        
    def validate_item(self, value):
        # Ensure the item exists
        if not Item.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Item does not exist")
        return value


class OrderSerializer(ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    total = SerializerMethodField()
    
    def get_total(self, obj):
        return obj.total

    class Meta:
        model = Order
        fields = ['id', 'status', 'user', 'created_at', 'order_items', 'total']



class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'



class DiscountSerializer(ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'



class RatingSerializer(ModelSerializer):
    item = ItemSerializer()
    user = CustomerSerializer()
    class Meta:
        model = Rating
        fields = [
            'id', 'review', 'rating', 'reviewed_at', 'item', 'user'
        ]



class CartSerializer(ModelSerializer):
    item = ItemSerializer()
    class Meta:
        model = Cart
        fields = ['id', 'item_quantity', 'discount', 'added_at', 'item']


class CartCreateSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'item', 'item_quantity', 'discount']
        
    def validate_item(self, value):
        # Ensure the item exists
        if not Item.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Item does not exist")
        return value

class BidSerializer(ModelSerializer):
    user = CustomerSerializer(read_only=True)
    
    class Meta:
        model = Bid
        fields = ['id', 'amount', 'status', 'user', 'used_item', 'created_at']
        raed_only_fields = ['id', 'created_at', 'user']
        
