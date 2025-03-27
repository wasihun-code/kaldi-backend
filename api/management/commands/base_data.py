from django.core.management.base import BaseCommand
from django.utils.timezone import now
from api.models import User, Address, Wallet, Item, Inventory, Order, Transaction, Discount, Cart, Bid
from decimal import Decimal
import random

def create_users():
    customers = []
    vendors = []
    
    for i in range(5):
        user = User.objects.create_user(
            username=f'customer{i}',
            email=f'customer{i}@example.com',
            phone=f'+123456789{i}',
            first_name=f'Customer{i}',
            last_name=f'Last{i}',
            user_type='customer',
            password='password'
        )
        customers.append(user)

    for i in range(3):
        user = User.objects.create_user(
            username=f'vendor{i}',
            email=f'vendor{i}@example.com',
            phone=f'+987654321{i}',
            first_name=f'Vendor{i}',
            last_name=f'Last{i}',
            user_type='vendor',
            business_name=f'Vendor Business {i}',
            password='password'
        )
        vendors.append(user)
    
    return customers, vendors

def create_addresses(users):
    for user in users:
        Address.objects.create(
            city='New York',
            state='NY',
            postal_code='10001',
            country='USA',
            user=user
        )

def create_wallets(users):
    for user in users:
        Wallet.objects.create(
            address=f'0x{random.randint(100000, 999999)}',
            balance=Decimal(random.uniform(10, 1000)),
            user=user
        )

def create_items(vendors):
    items = []
    for vendor in vendors:
        for i in range(3):
            item = Item.objects.create(
                name=f'Item {i} from {vendor.business_name}',
                description='A sample product',
                price=Decimal(random.uniform(20, 200)),
                vendor=vendor
            )
            items.append(item)
    return items

def create_inventory(items):
    for item in items:
        Inventory.objects.create(
            item_quantity=random.randint(1, 50),
            in_stock=True,
            location='Warehouse A',
            item=item
        )

def create_orders(customers, items):
    orders = []
    for customer in customers:
        order = Order.objects.create(
            status='pending',
            total=random.choice(items).price,
            user=customer
        )
        orders.append(order)
    return orders

def create_transactions(orders):
    for order in orders:
        Transaction.objects.create(
            transaction_hash=f'tx{random.randint(10000, 99999)}',
            status='pending',
            order=order,
            user=order.user
        )

def create_discounts(vendors):
    for vendor in vendors:
        Discount.objects.create(
            description='Special Offer',
            percentage=Decimal(random.uniform(5, 20)),
            expires_at=now().date(),
            vendor=vendor
        )

def create_carts(customers, items):
    for customer in customers:
        Cart.objects.create(
            item=random.choice(items),
            item_quantity=random.randint(1, 3),
            user=customer
        )

def create_bids(customers, items):
    for customer in customers:
        Bid.objects.create(
            amount=Decimal(random.uniform(10, 500)),
            status='bidding',
            item=random.choice(items),
            user=customer
        )

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        customers, vendors = create_users()
        create_addresses(customers + vendors)
        create_wallets(customers + vendors)
        items = create_items(vendors)
        create_inventory(items)
        orders = create_orders(customers, items)
        create_transactions(orders)
        create_discounts(vendors)
        create_carts(customers, items)
        create_bids(customers, items)
        self.stdout.write(self.style.SUCCESS('Database successfully populated!'))
