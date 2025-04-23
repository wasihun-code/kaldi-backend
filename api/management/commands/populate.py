from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware, now, timedelta
from django.db.utils import IntegrityError
from django.db import transaction
from api.models import (
    User, Address, Wallet, Item, Inventory, Order, 
    OrderItem, Transaction, Discount, Cart, Bid,
    Notification, Rating, UsedItem
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
            # Create users in separate transactions
            admin = self.create_admin()
            delivery_user = self.create_delivery_personnel(1)[0]
            customers = self.create_customers(10)
            vendors = self.create_vendors(8)
            
            all_users = customers + vendors + [delivery_user] + [admin]
            
            # Create addresses and wallets in batches
            self.create_addresses_in_batches(all_users)
            self.create_wallets_in_batches(all_users)
            
            # Create items and used items
            items = self.create_items_in_batches(vendors)
            used_items = self.create_used_items_in_batches(customers)
            
            # Create inventory for items
            self.create_inventory_in_batches(items)
            
            # Create orders, transactions, and related data
            orders = self.create_orders_in_batches(customers, items)
            self.create_transactions_in_batches(orders)
            
            # Create additional entities
            discounts = self.create_discounts_in_batches(vendors)
            self.create_carts_in_batches(customers, items, discounts)
            self.create_bids_in_batches(customers, used_items)
            self.create_notifications_in_batches(all_users)
            self.create_ratings_in_batches(customers, items)
            
            self.stdout.write(self.style.SUCCESS('Successfully populated database with realistic e-commerce data!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
            raise

    def create_admin(self):
        try:
            with transaction.atomic():
                self.stdout.write("Creating admin user...")
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
                with transaction.atomic():
                    first_name = fake.first_name()
                    last_name = fake.last_name()
                    username = f'delivery_{first_name.lower()}'
                    self.stdout.write(f"Creating delivery person {i+1}/{count}: {username}")
                    
                    user = User.objects.create_user(
                        username=username,
                        email=f'delivery.{first_name.lower()}@marketplace.com',
                        phone=fake.phone_number(),
                        first_name=first_name,
                        last_name=last_name,
                        user_type='delivery',
                        password='delivery123',
                        verification_status='verified',
                        business_name=f"{first_name}'s Delivery Service",
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
                with transaction.atomic():
                    first_name = fake.first_name()
                    last_name = fake.last_name()
                    email = f"{first_name.lower()}.{last_name.lower()}@customer.com"
                    username = f"{first_name.lower()}{last_name.lower()[:3]}{random.randint(1, 99)}"
                    
                    self.stdout.write(f"Creating customer {i+1}/{count}: {username}")
                    
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        phone=fake.phone_number(),
                        first_name=first_name,
                        last_name=last_name,
                        user_type='customer',
                        verification_status=random.choices(
                            ['verified', 'pending', 'unverified'],
                            weights=[0.7, 0.2, 0.1],
                            k=1
                        )[0],
                        business_name=None,
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
                with transaction.atomic():
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

    def create_addresses_in_batches(self, users, batch_size=10):
        us_states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]
        
        self.stdout.write("Creating addresses in batches...")
        
        for i in range(0, len(users), batch_size):
            batch_users = users[i:i+batch_size]
            addresses = []
            
            for user in batch_users:
                state = random.choice(us_states)
                city = fake.city()
                
                addresses.append(Address(
                    street_address=fake.street_address(),
                    city=city,
                    state=state,
                    postal_code=fake.postcode_in_state(state),
                    country='USA',
                    user=user
                ))
            
            try:
                with transaction.atomic():
                    Address.objects.bulk_create(addresses)
                    self.stdout.write(f"Created {len(addresses)} addresses (batch {i//batch_size + 1})")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating address batch: {e}'))

    def create_wallets_in_batches(self, users, batch_size=10):
        self.stdout.write("Creating wallets in batches...")
        
        for i in range(0, len(users), batch_size):
            batch_users = users[i:i+batch_size]
            wallets = []
            
            for user in batch_users:
                wallets.append(Wallet(
                    address=f'0x{random.randint(100000, 999999)}',
                    balance=Decimal(random.uniform(10, 1000)),
                    user=user
                ))
            
            try:
                with transaction.atomic():
                    Wallet.objects.bulk_create(wallets)
                    self.stdout.write(f"Created {len(wallets)} wallets (batch {i//batch_size + 1})")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating wallet batch: {e}'))

    def create_items_in_batches(self, vendors, batch_size=5):
        items = []
        all_items_data = []
        
        self.stdout.write("Creating items in batches...")
        
        # Prepare all item data first
        for vendor in vendors:
            # Choose a random category
            category = random.choice(list(PRODUCTS.keys()))
            # Create 1-10 items for this vendor
            num_items = random.randint(1, 10)
            # Select random products from that category
            products = random.sample(PRODUCTS[category], min(num_items, len(PRODUCTS[category])))
            
            for name, description, price in products:
                all_items_data.append({
                    'name': name,
                    'description': description,
                    'price': Decimal(price),
                    'category': category,
                    'vendor': vendor
                })
        
        # Create items in batches
        for i in range(0, len(all_items_data), batch_size):
            batch_items_data = all_items_data[i:i+batch_size]
            batch_items = []
            
            for item_data in batch_items_data:
                batch_items.append(Item(
                    name=item_data['name'],
                    description=item_data['description'],
                    price=item_data['price'],
                    category=item_data['category'],
                    vendor=item_data['vendor']
                ))
            
            try:
                with transaction.atomic():
                    created_items = Item.objects.bulk_create(batch_items)
                    items.extend(created_items)
                    self.stdout.write(f"Created {len(batch_items)} items (batch {i//batch_size + 1})")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating item batch: {e}'))
        
        return items

    def create_used_items_in_batches(self, customers, batch_size=5):
        used_items = []
        all_used_items_data = []
        
        self.stdout.write("Creating used items in batches...")
        
        # Prepare all used item data first
        for customer in customers:
            # Each customer has 1-3 used items
            num_items = random.randint(1, 3)
            # Choose a random category
            category = random.choice(list(PRODUCTS.keys()))
            # Select random products from that category
            products = random.sample(PRODUCTS[category], min(num_items, len(PRODUCTS[category])))
            
            for name, description, price in products:
                # Adjust price for used items (50-80% of original price)
                used_price = Decimal(price) * Decimal(random.uniform(0.5, 0.8))
                
                all_used_items_data.append({
                    'name': f"Used {name}",
                    'description': f"Pre-owned {description}. In good condition with minor signs of wear.",
                    'price': used_price.quantize(Decimal('0.00')),
                    'category': category,
                    'warranty_period': random.randint(1, 12),  # 1-12 months warranty
                    'user': customer
                })
        
        # Create used items in batches
        for i in range(0, len(all_used_items_data), batch_size):
            batch_used_items_data = all_used_items_data[i:i+batch_size]
            batch_used_items = []
            
            for item_data in batch_used_items_data:
                batch_used_items.append(UsedItem(
                    name=item_data['name'],
                    description=item_data['description'],
                    price=item_data['price'],
                    category=item_data['category'],
                    warranty_period=item_data['warranty_period'],
                    user=item_data['user']
                ))
            
            try:
                with transaction.atomic():
                    created_used_items = UsedItem.objects.bulk_create(batch_used_items)
                    used_items.extend(created_used_items)
                    self.stdout.write(f"Created {len(batch_used_items)} used items (batch {i//batch_size + 1})")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating used item batch: {e}'))
        
        return used_items

    def create_inventory_in_batches(self, items, batch_size=10):
        self.stdout.write("Creating inventory in batches...")
        
        for i in range(0, len(items), batch_size):
            batch_items = items[i:i+batch_size]
            inventories = []
            
            for item in batch_items:
                # 70% chance of being in stock, 30% out of stock
                in_stock = random.random() < 0.7
                item_quantity = random.randint(1, 50) if in_stock else 0
                
                inventories.append(Inventory(
                    item=item,
                    item_quantity=item_quantity,
                    in_stock=in_stock,
                    location=random.choice(['Warehouse A', 'Warehouse B', 'Store']),
                    last_restocked=now() - timedelta(days=random.randint(0, 30))
                ))
            
            try:
                with transaction.atomic():
                    Inventory.objects.bulk_create(inventories)
                    self.stdout.write(f"Created {len(inventories)} inventory records (batch {i//batch_size + 1})")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating inventory batch: {e}'))

    def create_orders_in_batches(self, customers, items, batch_size=5):
        orders = []
        self.stdout.write("Creating orders in batches...")
        
        for customer in customers:
            try:
                with transaction.atomic():
                    # Each customer has 1-3 orders
                    num_orders = random.randint(1, 3)
                    
                    for _ in range(num_orders):
                        # Create the order
                        order = Order.objects.create(
                            status=random.choice(['pending', 'shipped', 'delivered']),
                            user=customer
                        )
                        
                        # Add 1-3 random items to the order
                        num_items = min(random.randint(1, 3), len(items))
                        if num_items > 0:
                            selected_items = random.sample(list(items), num_items)
                            
                            order_items = []
                            for item in selected_items:
                                order_items.append(OrderItem(
                                    order=order,
                                    item=item,
                                    quantity=random.randint(1, 5),
                                    price_at_purchase=item.price
                                ))
                            
                            OrderItem.objects.bulk_create(order_items)
                        
                        orders.append(order)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating order for customer {customer.id}: {e}'))
        
        return orders

    def create_transactions_in_batches(self, orders, batch_size=10):
        self.stdout.write("Creating transactions in batches...")
        
        for i in range(0, len(orders), batch_size):
            batch_orders = orders[i:i+batch_size]
            transactions = []
            
            for order in batch_orders:
                transactions.append(Transaction(
                    transaction_hash=f'tx{random.randint(10000, 99999)}',
                    status='completed' if order.status == 'delivered' else 
                          'failed' if random.random() < 0.1 else 'pending',
                    order=order,
                    user=order.user
                ))
            
            try:
                with transaction.atomic():
                    Transaction.objects.bulk_create(transactions)
                    self.stdout.write(f"Created {len(transactions)} transactions (batch {i//batch_size + 1})")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating transaction batch: {e}'))

    def create_discounts_in_batches(self, vendors):
        discounts = []
        discount_types = [
            ('SUMMER25', 'Summer Sale', 25, 100),
            ('FALL20', 'Fall Special', 20, 50),
            ('WELCOME10', 'New Customer Discount', 10, 200),
            ('LOYALTY15', 'Loyalty Reward', 15, 150),
            ('CLEARANCE30', 'Clearance Event', 30, 75)
        ]
        
        self.stdout.write("Creating discounts...")
        
        for vendor in vendors:
            try:
                with transaction.atomic():
                    # Each vendor has 1-3 unique discounts
                    num_discounts = random.randint(1, 3)
                    for i in range(num_discounts):
                        code, desc, base_percent, base_redemptions = random.choice(discount_types)
                        discount_code = f"{code}{random.randint(10, 99)}"
                        
                        self.stdout.write(f"Creating discount for {vendor.business_name}: {discount_code}")
                        
                        discount = Discount.objects.create(
                            code=discount_code,
                            name=f"{vendor.business_name} {desc}",
                            percentage=Decimal(base_percent * random.uniform(0.8, 1.2)).quantize(Decimal('1')),
                            expires_at=now().date() + timedelta(days=random.randint(7, 60)),
                            vendor=vendor,
                            max_redemptions=base_redemptions,
                        )
                        discounts.append(discount)
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f'Skipping duplicate discount code: {e}'))
                continue
        
        return discounts

    def create_carts_in_batches(self, customers, items, discounts, batch_size=10):
        self.stdout.write("Creating carts...")
        
        # Get all items that are in stock
        in_stock_items = [i for i in items if hasattr(i, 'inventory') and i.inventory.in_stock]
        
        if not in_stock_items:
            self.stdout.write(self.style.WARNING('No items in stock to create carts'))
            return

        for customer in customers:
            try:
                with transaction.atomic():
                    # Each customer has 1 cart with 1-10 items
                    num_items = random.randint(1, min(10, len(in_stock_items)))
                    selected_items = random.sample(in_stock_items, num_items)
                    
                    cart_items = []
                    for item in selected_items:
                        cart_items.append(Cart(
                            item=item,
                            item_quantity=random.randint(1, 3),
                            user=customer,
                            discount=random.choice(discounts) if random.random() < 0.2 and discounts else None,
                            added_at=now() - timedelta(days=random.randint(0, 30))
                        ))
                    
                    Cart.objects.bulk_create(cart_items)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating cart for customer {customer.id}: {e}'))

    def create_bids_in_batches(self, customers, used_items, batch_size=20):
        all_bids = []
        
        self.stdout.write("Creating bids...")
        
        for used_item in used_items:
            # Get potential bidders (all customers except the owner)
            potential_bidders = [c for c in customers if c != used_item.user]
            
            if not potential_bidders:
                continue
                
            # Each used item gets 1-3 bids from different customers
            num_bids = random.randint(1, 3)
            bidders = random.sample(potential_bidders, min(num_bids, len(potential_bidders)))
            
            for bidder in bidders:
                all_bids.append({
                    'amount': used_item.price * Decimal(random.uniform(0.8, 1.5)).quantize(Decimal('0.00')),
                    'status': 'completed' if random.random() < 0.2 else 'bidding',
                    'used_item': used_item,
                    'user': bidder,
                    'created_at': now() - timedelta(days=random.randint(0, 30))
                })
        
        for i in range(0, len(all_bids), batch_size):
            batch_bids_data = all_bids[i:i+batch_size]
            batch_bids = []
            
            for bid_data in batch_bids_data:
                batch_bids.append(Bid(
                    amount=bid_data['amount'],
                    status=bid_data['status'],
                    used_item=bid_data['used_item'],
                    user=bid_data['user'],
                    created_at=bid_data['created_at']
                ))
            
            try:
                with transaction.atomic():
                    Bid.objects.bulk_create(batch_bids)
                    self.stdout.write(f"Created {len(batch_bids)} bids (batch {i//batch_size + 1})")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating bid batch: {e}'))

    def create_notifications_in_batches(self, users, batch_size=50):
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
        
        all_notifications = []
        self.stdout.write("Creating notifications...")
        
        for user in users:
            # Each user gets 1-3 notifications
            num_notifications = random.randint(1, 3)
            for _ in range(num_notifications):
                all_notifications.append({
                    'type': random.choice(notification_types),
                    'read': random.random() < 0.7,
                    'text': random.choice(messages),
                    'user': user,
                    'notified_at': now() - timedelta(days=random.randint(0, 90))
                })
        
        for i in range(0, len(all_notifications), batch_size):
            batch_notifications_data = all_notifications[i:i+batch_size]
            batch_notifications = []
            
            for notification_data in batch_notifications_data:
                batch_notifications.append(Notification(
                    type=notification_data['type'],
                    read=notification_data['read'],
                    text=notification_data['text'],
                    user=notification_data['user'],
                    notified_at=notification_data['notified_at']
                ))
            
            try:
                with transaction.atomic():
                    Notification.objects.bulk_create(batch_notifications)
                    self.stdout.write(f"Created {len(batch_notifications)} notifications (batch {i//batch_size + 1})")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating notification batch: {e}'))

    def create_ratings_in_batches(self, customers, items, batch_size=20):
        all_ratings = []
        
        self.stdout.write("Creating ratings in batches...")
        
        for customer in customers:
            # Each customer rates 3-4 random items
            num_ratings = random.randint(3, 4)
            rated_items = random.sample(list(items), min(num_ratings, len(items)))
            
            for item in rated_items:
                rating_value = random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[0.05, 0.1, 0.15, 0.3, 0.4],
                    k=1
                )[0]
                
                all_ratings.append({
                    'rating': rating_value,
                    'review': fake.paragraph(nb_sentences=2) if random.random() < 0.8 else '',
                    'item': item,
                    'user': customer,
                    'reviewed_at': now() - timedelta(days=random.randint(0, 180))
                })
        
        for i in range(0, len(all_ratings), batch_size):
            batch_ratings_data = all_ratings[i:i+batch_size]
            batch_ratings = []
            
            for rating_data in batch_ratings_data:
                batch_ratings.append(Rating(
                    rating=rating_data['rating'],
                    review=rating_data['review'],
                    item=rating_data['item'],
                    user=rating_data['user'],
                    reviewed_at=rating_data['reviewed_at']
                ))
            
            try:
                with transaction.atomic():
                    Rating.objects.bulk_create(batch_ratings)
                    self.stdout.write(f"Created {len(batch_ratings)} ratings (batch {i//batch_size + 1})")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating rating batch: {e}'))