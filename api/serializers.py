from rest_framework.serializers import ModelSerializer, SerializerMethodField


from api.models import (
    Address, Transaction, Order, Wallet,
    Inventory, Discount, Item,
    Cart, Bid, User, OrderItem
)



class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'



class VendorSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone', 
            'business_name', 'vendor_type', 'bussiness_license' 
        ]



class CustomerSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone']
        # read_only_fields = ('id')        



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



class OrderItemSerializer(ModelSerializer):
    item = ItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'quantity', 'price_at_purchase']



class OrderSerializer(ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    total = SerializerMethodField()
    
    def get_total(self, obj):
        return obj.total

    class Meta:
        model = Order
        fields = ['id', 'status', 'user', 'created_at', 'updated_at', 'order_items', 'total']



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
