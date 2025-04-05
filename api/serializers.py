from rest_framework.serializers import ModelSerializer

from api.models import (
    Address, Transaction, Order, Wallet,
    Inventory, Discount, Item,
    Cart, Bid, User
)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id', 'is_active', 'is_staff', 'is_superuser')


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class WalletSerializer(ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class InventorySerializer(ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class DiscountSerializer(ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class BidSerializer(ModelSerializer):
    class Meta:
        model = Bid
        fields = '__all__'
