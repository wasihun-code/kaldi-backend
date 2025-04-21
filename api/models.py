from django.contrib.auth.context_processors import auth
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
        ('delivery', 'Delivery'),
    ]

    STATUS_CHOICES = [
        ('verified', 'Verified'),
        ('pending', 'Pending'),
        ('unverified', 'Unverified'),
    ]

    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    user_type = models.CharField(choices=USER_CHOICES, max_length=10, default='customer')

    business_name = models.CharField(max_length=50, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    verification_status = models.CharField(choices=STATUS_CHOICES, max_length=15, default='unverified')
    vendor_type = models.CharField(
        max_length=10,
        choices=[('individual', 'Individual'), ('business', 'Business')], 
        default='individual',
        null=True, 
        blank=True
    )
    business_license = models.CharField(max_length=50, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def __str__(self):
        return f'{self.user_type} - {self.id} : {self.first_name} {self.last_name}'


    class Meta:
        abstract = False



class Address(models.Model):
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_address', blank=True, null=True)
    street_address = models.CharField(max_length=100)

    def __str__(self):
        return (
            f'Address - {self.user.business_name if self.user.user_type == "vendor" else self.user.first_name + " " + self.user.last_name}, '
            f'{self.city}, {self.state}, {self.country}'
            
        )



class Wallet(models.Model):
    address = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    connected_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_wallet', blank=True, null=True)

    def __str__(self):
        return (
            f'Wallet - {self.user.business_name if self.user.user_type == "vendor" else self.user.first_name + " " + self.user.last_name}, '
            f'Address: {self.address}, '
            f'Balance: {self.balance}'
        )




class Item(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('home', 'Home'),
        ('books', 'Books'),
        ('toys', 'Toys'),
        ('sports', 'Sports'),
        ('jewelry', 'Jewelry'),
    ]
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='electronics')  # Add this field
    created_at = models.DateTimeField(auto_now_add=True) 
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return f'{self.name} - ${self.price} by Vendor {self.vendor.business_name}'
    

class UsedItem(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('home', 'Home'),
        ('books', 'Books'),
        ('toys', 'Toys'),
        ('sports', 'Sports'),
        ('jewelry', 'Jewelry'),
    ]
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=Item.CATEGORY_CHOICES, default='electronics')
    warranty_period = models.IntegerField() # in months
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='used_items')
    
    def __str__(self):
        return (
            f'Used Item Detail: '
            f'{self.name} - ${self.price} - Warranty: {self.warranty_period} months'
        )


class Inventory(models.Model):
    item_quantity = models.PositiveIntegerField()
    in_stock = models.BooleanField(default=True)
    location = models.CharField(max_length=50)
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='inventory')
    last_restocked = models.DateTimeField(null=True, blank=True)  # Add this field


    def __str__(self):
        return f'{self.item.name} - {self.item_quantity} available items'



class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    @property
    def total(self):
        return sum(item.price_at_purchase * item.quantity for item in self.order_items.all())

    def __str__(self):
        return f"Order #{self.id} - {self.status} by {self.user.email}"      



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=4)
    
    def __str__(self):
        return f"{self.quantity} x {self.item.name} in Order {self.order.id}"
    


class Transaction(models.Model):
    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('completed', 'Completed')
    ]
    transaction_hash = models.CharField(unique=True, max_length=100)
    status = models.CharField(choices=TRANSACTION_STATUS_CHOICES, max_length=10, default='pending')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return (
            f'Transaction {self.transaction_hash} - {self.status} '
            f'on Order {self.order.id} '
            f'by User {self.user.first_name} {self.user.last_name}'
        )




class Discount(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    expires_at = models.DateField()
    added_at = models.DateTimeField(auto_now_add=True)  # Add this field
    redemptions = models.IntegerField(default=0, null=True, blank=True)
    max_redemptions = models.IntegerField()
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discounts')

    def __str__(self):
        return f'{self.percentage}% off by {self.vendor.business_name}'



class Cart(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='cart_items')
    item_quantity = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_discounts')
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Cart of {self.user.first_name} - {self.item_quantity} x {self.item.name}'




class Bid(models.Model):
    STATUS_CHOICES = [
        ('bidding', 'Bidding'),
        ('completed', 'Bidding Completed'),
    ]
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICES, max_length=15, default='bidding')
    created_at = models.DateTimeField(auto_now_add=True)  
    used_item = models.ForeignKey(UsedItem, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')

    def __str__(self):
        return (
            f'Bid of {self.amount} '
            f'on {self.used_item.name} '
            f'by {self.user.first_name} {self.user.last_name} - ${self.amount}'
        )




class Notification(models.Model):
    NOTIFICATION_CHOICES = [
        ('system', 'System'),
        ('general', 'General'),
        ('product', 'Product'),
        ('archived','Archived')
    ]
    type = models.CharField(choices=NOTIFICATION_CHOICES, default='general', max_length=15)
    notified_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField()
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')  # Add this field

    def __str__(self):
        return f'{self.type} notification for {self.user.first_name}: {self.text[:30]}...'


class Rating(models.Model):
    rating = models.IntegerField()
    review = models.TextField()
    reviewed_at = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')

    def __str__(self):
        return (
            f'Rating {self.rating} for {self.item.name} '
            f'by {self.user.first_name} {self.user.last_name} '
            f'Review Text: {self.review}'
        )


