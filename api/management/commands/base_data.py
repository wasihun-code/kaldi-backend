from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware, now, timedelta
from django.db.utils import IntegrityError
from django.db import transaction
from api.models import (
    User, Address, Wallet, Item, Inventory, Order, 
    OrderItem, Transaction, Discount, Cart, Bid,
    Notification, Rating
)
from decimal import Decimal
import random
from faker import Faker
import uuid
from faker.providers import company, address, person, phone_number, lorem
import re

fake = Faker()
fake.add_provider(company)
fake.add_provider(address)
fake.add_provider(person)
fake.add_provider(phone_number)
fake.add_provider(lorem)

# Real-world product data by category
PRODUCTS = {
    'electronics': [
        ('iPhone 15 Pro', 'Latest Apple smartphone with A17 Pro chip', 999.99),
        ('Samsung Galaxy S23', 'Premium Android smartphone', 799.99),
        ('Sony WH-1000XM5', 'Noise-cancelling wireless headphones', 349.99),
        ('MacBook Air M2', 'Thin and light laptop with Apple silicon', 1099.00),
        ('Dyson V15 Detect', 'Cordless vacuum cleaner with laser dust detection', 699.99)
    ],
'clothing': [
        ('Nike Air Force 1', 'Classic white sneakers', 110.00),
        ('Levi\'s 501 Jeans', 'Original fit jeans', 59.50),
        ('Patagonia Nano Puff', 'Lightweight insulated jacket', 199.00),
        ('Ralph Lauren Polo Shirt', 'Classic cotton polo', 89.50),
        ('Adidas Ultraboost', 'Running shoes with Boost technology', 180.00)
    ],
    'home': [
        ('Instant Pot Duo', '7-in-1 electric pressure cooker', 99.95),
        ('Nespresso Vertuo', 'Coffee machine with centrifusion technology', 179.00),
        ('Cuisinart Food Processor', '12-cup capacity with multiple blades', 199.95),
        ('All-Clad Stainless Cookware', '5-piece cookware set', 399.99),
        ('Dyson Pure Cool', 'Air purifier and fan', 449.99)
    ],
    'books': [
        ('Atomic Habits', 'James Clear - Build good habits and break bad ones', 14.99),
        ('The Midnight Library', 'Matt Haig - Novel about life choices', 13.99),
        ('Dune', 'Frank Herbert - Sci-fi classic', 9.99),
        ('Sapiens', 'Yuval Noah Harari - Brief history of humankind', 17.99),
        ('The Silent Patient', 'Alex Michaelides - Psychological thriller', 12.99)
    ],
    'toys': [
        ('LEGO Star Wars Millennium Falcon', 'Iconic starship building set', 159.99),
        ('Nintendo Switch', 'Hybrid gaming console', 299.99),
        ('Barbie Dreamhouse', '3-story dollhouse with accessories', 199.99),
        ('Hot Wheels Ultimate Garage', '5-foot tall car playset', 179.99),
        ('Play-Doh Kitchen Creations', 'Stovetop playset with 10 cans', 24.99)
    ],
    'sports': [
        ('Yeti Rambler 20oz', 'Vacuum insulated stainless steel tumbler', 39.99),
        ('Peloton Bike', 'Connected fitness bike with classes', 1445.00),
        ('Wilson NFL Official Football', 'Leather football', 99.99),
        ('Callaway Golf Set', 'Complete set for beginners', 399.99),
        ('Hydro Flask Water Bottle', '32oz wide mouth bottle', 44.95)
    ],
    'jewelry': [
        ('Pandora Moments Bracelet', 'Sterling silver charm bracelet', 65.00),
        ('Tiffany & Co. Heart Tag Pendant', 'Sterling silver necklace', 150.00),
        ('Apple Watch Series 9', 'Smartwatch with aluminum case', 399.00),
        ('David Yurman Cable Bracelet', 'Sterling silver with gold accents', 395.00),
        ('Cartier Love Bracelet', 'Iconic screw motif bracelet', 6350.00)
    ]}

def clean_email_domain(name):
    """Clean up a string to be a valid domain-like name"""
    # Remove apostrophes and non-word characters
    name = re.sub(r"[^\w]", "", name)
    # Lowercase everything
    return name.lower()

class Command(BaseCommand):
    help = 'Populate database with realistic e-commerce data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating realistic e-commerce data...")
        
        try:
            with transaction.atomic():
                # Create admin
                self.stdout.write("Creating admin user...")
                admin = self.create_admin()
                
                # Create delivery personnel
                self.stdout.write("Creating delivery personnel...")
                delivery_users = self.create_delivery_personnel(3)
                
                # Create customers and vendors
                self.stdout.write("Creating customers...")
                customers = self.create_customers(25)
                self.stdout.write("Creating vendors...")
                vendors = self.create_vendors(8)
                
                # Create addresses for all users
                self.stdout.write("Creating addresses...")
                self.create_addresses(customers + vendors + delivery_users + [admin])
                
                # Create wallets
                self.stdout.write("Creating wallets...")
                self.create_wallets(customers + vendors + delivery_users + [admin])
                
                # Create items with realistic products
                self.stdout.write("Creating items...")
                items = self.create_items(vendors)
                
                # Create inventory
                self.stdout.write("Creating inventory...")
                self.create_inventory(items)
                
                # Create orders with realistic patterns
                self.stdout.write("Creating orders...")
                orders = self.create_orders(customers, items)
                
                # Create transactions
                self.stdout.write("Creating transactions...")
                self.create_transactions(orders)
                
                # Create discounts
                self.stdout.write("Creating discounts...")
                discounts = self.create_discounts(vendors)
                
                # Create shopping carts
                self.stdout.write("Creating carts...")
                self.create_carts(customers, items, discounts)
                
                # Create bids
                self.stdout.write("Creating bids...")
                self.create_bids(customers, items)
                
                # Create notifications
                self.stdout.write("Creating notifications...")
                self.create_notifications(customers + vendors + delivery_users + [admin])
                
                # Create ratings and reviews
                self.stdout.write("Creating ratings...")
                self.create_ratings(customers, items)
                
                self.stdout.write(self.style.SUCCESS('Successfully populated database with realistic e-commerce data!'))
        
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'IntegrityError: {str(e)}'))
            self.stdout.write(self.style.ERROR('Rolling back all changes due to error...'))
            raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
            raise

    def clean_email_domain(name):
        """Clean up a string to be a valid domain-like name"""
        # Remove apostrophes and non-word characters
        name = re.sub(r"[^\w]", "", name)
        # Lowercase everything
        return name.lower()

    def create_admin(self):
        try:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@marketplace.com',
                phone='+18885551234',
                first_name='Admin',
                last_name='User',
                user_type='admin',
                password='admin123',
                business_name='Marketplace Admin',
                verification_status='verified'
            )
            admin.set_password('admin123')
            admin.save()
            return admin
        except IntegrityError as e:
            self.stdout.write(self.style.WARNING(f'Admin user already exists: {e}'))
            return User.objects.get(username='admin')

    def create_delivery_personnel(self, count):
        delivery_users = []
        for i in range(count):
            try:
                username = fake.user_name()
                self.stdout.write(f"Creating delivery person {i+1}/{count}: {username}")
                
                user = User.objects.create_user(
                    username=username,
                    email=fake.email(),
                    phone=fake.phone_number(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    user_type='delivery',
                    password='delivery123',
                    verification_status='verified'
                )
                user.set_password('delivery123')
                user.save()
                delivery_users.append(user)
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f'Skipping duplicate delivery user: {e}'))
                continue
        return delivery_users

    def create_customers(self, count):
        customers = []
        for i in range(count):
            try:
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = f"{first_name.lower()}.{last_name.lower()}@example.com"
                username = f"{first_name.lower()}{random.randint(1, 9999)}"
                
                self.stdout.write(f"Creating customer {i+1}/{count}: {username}")
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    phone=fake.phone_number(),
                    first_name=first_name,
                    last_name=last_name,
                    user_type='customer',
                    password='customer123',
                    verification_status=random.choices(
                        ['verified', 'pending', 'unverified'],
                        weights=[0.7, 0.2, 0.1],
                        k=1
                    )[0],
                    profile_image=None if random.random() < 0.7 else f'profile_images/user_{uuid.uuid4().hex[:8]}.jpg'
                )
                user.set_password('customer123')
                user.save()
                customers.append(user)
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f'Skipping duplicate customer: {e}'))
                continue
        return customers

    def create_vendors(self, count):
        vendors = []
        for i in range(count):
            try:
                vendor_type = random.choice(['individual', 'business'])
                if vendor_type == 'individual':
                    first_name = fake.first_name()
                    last_name = fake.last_name()
                    business_name = f"{first_name}'s {fake.word().capitalize()} Shop"
                else:
                    first_name = ''
                    last_name = ''
                    business_name = fake.company()
                
                clean_business = clean_email_domain(business_name)
                username = f"{clean_business}"
                self.stdout.write(f"Creating vendor {i+1}/{count}: {business_name}")
                
                user = User.objects.create_user(
                    username=username,
                    email=f"contact@{clean_business}.com",
                    phone=fake.phone_number(),
                    first_name=first_name,
                    last_name=last_name,
                    user_type='vendor',
                    business_name=business_name,
                    password='vendor123',
                    verification_status=random.choices(
                        ['verified', 'pending', 'unverified'],
                        weights=[0.6, 0.3, 0.1],
                        k=1
                    )[0],
                    vendor_type=vendor_type,
                    business_license=None if random.random() < 0.3 else str(uuid.uuid4()).replace('-', '')[:15],
                    rating=Decimal(random.uniform(3.5, 5.0)).quantize(Decimal('0.01'))
                )
                user.set_password('vendor123')
                user.save()
                vendors.append(user)
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f'Skipping duplicate vendor: {e}'))
                continue
        return vendors

 

    def create_wallets(self, users):
        for user in users:
            try:
                Wallet.objects.create(
                    address=f'0x{random.randint(100000, 999999)}',
                    balance=Decimal(random.uniform(10, 1000)),
                    user=user
                )
            except Exception as e:
                print(f"Error creating wallet for user {user.id}: {e}")

    def create_items(self, vendors):
        items = []
        for vendor in vendors:
            for i in range(3):
                try:
                    item = Item.objects.create(
                        name=f'Item {i} from {vendor.business_name}',
                        description='A sample product',
                        price=Decimal(random.uniform(20, 200)),
                        vendor=vendor
                    )
                    items.append(item)
                except Exception as e:
                    print(f"Error creating item for vendor {vendor.id}: {e}")
        return items

    def create_orders(self, customers, items):
        orders = []
        for customer in customers:
            try:
                # First create the order
                order = Order.objects.create(
                    status=random.choice(['pending', 'shipped', 'delivered']),
                    user=customer
                )
                
                # Then add 1-3 random items to the order
                num_items = random.randint(1, 3)
                selected_items = random.sample(items, num_items)
                
                for item in selected_items:
                    try:
                        OrderItem.objects.create(
                            order=order,
                            item=item,
                            quantity=random.randint(1, 5),
                            price_at_purchase=item.price  # Store the price at time of purchase
                        )
                    except Exception as e:
                        print(f"Error adding item {item.id} to order {order.id}: {e}")
                
                orders.append(order)
            except Exception as e:
                print(f"Error creating order for customer {customer.id}: {e}")
        return orders

    def create_transactions(self, orders):
        for order in orders:
            try:
                Transaction.objects.create(
                    transaction_hash=f'tx{random.randint(10000, 99999)}',
                    status=random.choice(['pending', 'completed', 'failed']),
                    order=order,
                    user=order.user
                )
            except Exception as e:
                print(f"Error creating transaction for order {order.id}: {e}")

    def create_inventory(self, items):
        for item in items:
            try:
                Inventory.objects.create(
                    item_quantity=random.randint(1, 50),
                    in_stock=True,
                    location='Warehouse A',
                    item=item
                )
            except Exception as e:
                print(f"Error creating inventory for item {item.id}: {e}")

    def create_addresses(self, users):
        us_states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]
        
        for user in users:
            try:
                state = random.choice(us_states)
                city = fake.city()
                
                Address.objects.create(
                    street_address=fake.street_address(),
                    city=city,
                    state=state,
                    postal_code=fake.postcode_in_state(state),
                    country='USA',
                    user=user
                )
            except Exception as e:
                print(f"Error creating address for user {user.id}: {e}")



    def create_discounts(self, vendors):
        discounts = []
        discount_types = [
            ('SUMMER25', 'Summer Sale', 25),
            ('FALL20', 'Fall Special', 20),
            ('WELCOME10', 'New Customer Discount', 10),
            ('LOYALTY15', 'Loyalty Reward', 15),
            ('CLEARANCE30', 'Clearance Event', 30)
        ]
        
        for vendor in vendors:
            for i in range(random.randint(1, 3)):
                try:
                    code, desc, base_percent = random.choice(discount_types)
                    discount_code = f"{code}{random.randint(10, 99)}"
                    
                    self.stdout.write(f"Creating discount for {vendor.business_name}: {discount_code}")
                    
                    discount = Discount.objects.create(
                        code=discount_code,
                        description=desc,
                        percentage=Decimal(base_percent * random.uniform(0.8, 1.2)).quantize(Decimal('1')),
                        expires_at=now().date() + timedelta(days=random.randint(7, 60)),
                        vendor=vendor,
                        created_at=now() - timedelta(days=random.randint(1, 30))
                    )
                    discounts.append(discount)
                except IntegrityError as e:
                    self.stdout.write(self.style.WARNING(f'Skipping duplicate discount code: {e}'))
                    continue
        return discounts


    def create_carts(self, customers, items, discounts):
        # 60% of customers have carts with 1-4 items
        for customer in random.sample(customers, k=int(len(customers) * 0.6)):
            for _ in range(random.randint(1, 4)):
                item = random.choice([i for i in items if i.inventory.in_stock])
                Cart.objects.create(
                    item=item,
                    item_quantity=random.randint(1, 3),
                    user=customer,
                    discount=random.choice(discounts) if random.random() < 0.2 and discounts else None,
                    added_at=now() - timedelta(days=random.randint(0, 30))
                )

    def create_bids(self, customers, items):
        # 30% of items have bids from 3-8 customers
        bid_items = random.sample(items, k=int(len(items) * 0.3))
        
        for item in bid_items:
            bidders = random.sample(customers, k=random.randint(3, 8))
            for bidder in bidders:
                Bid.objects.create(
                    amount=item.price * Decimal(random.uniform(0.8, 1.5)).quantize(Decimal('0.00')),
                    status='completed' if random.random() < 0.2 else 'bidding',
                    item=item,
                    user=bidder,
                    created_at=now() - timedelta(days=random.randint(0, 30))
                )

    def create_notifications(self, users):
        notification_types = ['system', 'general', 'product', 'archived']
        messages = [
            "Your order has shipped",
            "New items from your favorite brands",
            "Your review was helpful to others",
            "Special discount just for you",
            "Your account was accessed from a new device",
            "Your bid was accepted",
            "Inventory alert for your wishlist item",
            "Payment confirmation",
            "Delivery update",
            "Welcome to our marketplace!"
        ]
        
        for user in users:
            for _ in range(random.randint(3, 10)):
                Notification.objects.create(
                    type=random.choice(notification_types),
                    read=random.random() < 0.7,
                    text=random.choice(messages),
                    user=user,
                    notified_at=now() - timedelta(days=random.randint(0, 90))
                )

    def create_ratings(self, customers, items):
        # 70% of items have 1-5 ratings
        rated_items = random.sample(items, k=int(len(items) * 0.7))
        
        for item in rated_items:
            reviewers = random.sample(customers, k=random.randint(1, 5))
            for reviewer in reviewers:
                rating_value = random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[0.05, 0.1, 0.15, 0.3, 0.4],
                    k=1
                )[0]
                
                Rating.objects.create(
                    rating=rating_value,
                    review=fake.paragraph(nb_sentences=2) if random.random() < 0.8 else '',
                    item=item,
                    user=reviewer,
                    reviewed_at=now() - timedelta(days=random.randint(0, 180))
                )