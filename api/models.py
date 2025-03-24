from django.contrib.auth.context_processors import auth
from django.db import models
from django.contrib.auth.models import AbstractUser
# Choice Constants


class BaseUser(AbstractUser):
    USER_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor')
    ]
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    user_type = models.CharField(choices=USER_CHOICES, max_length=10, default='customer')

    USERNAME_FIELD = 'email'  # Login with email instead of username
    REQUIRED_FIELDS = ['username', 'phone', 'first_name', 'last_name']

    def __str__(self):
        return f'{self.user_type} - {self.id} : {self.first_name} {self.last_name}'

    class Meta:
        abstract = True  # Prevents direct table creation


class Customer(BaseUser):
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customer_users",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customer_users",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )


class Vendor(BaseUser):
    STATUS_CHOICES = [
        ('verified', 'Verified'),
        ('pending', 'Pending'),
        ('unverified', 'Unverified'),
    ]
    business_name = models.CharField(max_length=50)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    verification_status = models.CharField(choices=STATUS_CHOICES, max_length=15, default='unverified')
    vendor_type = models.CharField(max_length=10, choices=[('individual', 'Individual'), ('business', 'Business')], default='individual')
    business_license = models.CharField(max_length=50, null=True, blank=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="vendor_users",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="vendor_users",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )


class Address(models.Model):
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=20)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='user_address', blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_address', blank=True, null=True)

    def __str__(self):
        return (
            f'Address ({'Vendor: ' + self.vendor.business_name if self.vendor else 'Customer: ' + self.customer.first_name + ' ' + self.customer.last_name})'
            f'{self.city}, {self.state}, {self.country}'
        )


class Wallet(models.Model):
    address = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    connected_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='user_wallet', blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_wallet', blank=True, null=True)

    def __str__(self):
        return (
            f'Wallet ({'Vendor: ' + self.vendor.business_name if self.vendor else 'Customer: ' + self.customer.first_name + ' ' + self.customer.last_name})'
            f'Address: {self.address}'
            f'Balance: {self.balance}'
        )


class Item(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return f'{self.name} - ${self.price} by Vendor {self.vendor.business_name}'


class Inventory(models.Model):
    item_quantity = models.PositiveIntegerField()
    in_stock = models.BooleanField(default=True)
    location = models.CharField(max_length=50)
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='inventory')

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
    total = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return (
            f'Order {self.id} - {self.status} - Total: ${self.total}'
            f'by {self.customer.first_name} {self.customer.last_name}'
        )


class Transaction(models.Model):
    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('completed', 'Completed')
    ]
    transaction_hash = models.CharField(unique=True, max_length=100)
    status = models.CharField(choices=TRANSACTION_STATUS_CHOICES, max_length=10, default='pending')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transactions')

    def __str__(self):
        return (
            f'Transaction {self.transaction_hash} - {self.status} '
            f'on Order {self.order.id} '
            f'by Customer {self.customer.first_name} {self.customer.last_name}'
        )


class Discount(models.Model):
    description = models.CharField(max_length=50)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    expires_at = models.DateField()
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='discounts')

    def __str__(self):
        return f'{self.percentage}% off by {self.vendor.business_name}'


class Cart(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='cart_items')
    item_quantity = models.PositiveIntegerField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cart')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_discounts')

    def __str__(self):
        return f'Cart of {self.customer} - {self.item_quantity} x {self.item.name}'


class Bid(models.Model):
    STATUS_CHOICES = [
        ('bidding', 'Bidding'),
        ('completed', 'Bidding Completed'),
    ]
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICES, max_length=15, default='bidding')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='bids')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bids')

    def __str__(self):
        return (
            f'Bid of {self.amount} '
            f'on {self.item.name} '
            f'by {self.customer.first_name} {self.customer.last_name} - ${self.amount}'
        )
