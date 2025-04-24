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
import os
from django.conf import settings

fake = Faker()
fake.add_provider(company)
fake.add_provider(address)
fake.add_provider(person)
fake.add_provider(phone_number)
fake.add_provider(lorem)

# Real-world product data by category with enhanced descriptions
PRODUCTS = {
    'electronics': [
        ('iPhone 15 Pro Max', 'Apple\'s flagship smartphone featuring a 6.7" Super Retina XDR display, A17 Pro chip, 48MP camera system, and titanium design. All-day battery life and iOS 18.', 1199.99, 'iphone15pro.jpg'),
        ('Samsung Galaxy S24 Ultra', 'The ultimate Galaxy experience with S Pen, 200MP camera, Snapdragon 8 Gen 3 processor, and 6.8" QHD+ Dynamic AMOLED 2X display. Features Galaxy AI for enhanced productivity.', 1299.99, 'galaxy_s24.jpg'),
        ('Sony WH-1000XM5', 'Industry-leading noise cancellation headphones with 30-hour battery life, crystal clear calls, and exceptional sound quality. Features auto noise cancelling optimizer and quick charging.', 399.99, 'sony_wh1000xm5.jpg'),
        ('MacBook Air M3', 'Impossibly thin laptop powered by the M3 chip. Features a stunning 13.6" Liquid Retina display, 18-hour battery life, and 8-core CPU for blazing-fast performance.', 1299.00, 'macbook_air.jpg'),
        ('iPad Pro 13"', 'The most advanced iPad ever, featuring the M2 chip, Liquid Retina XDR display, Pro cameras with LiDAR, Thunderbolt port, and support for Apple Pencil and Magic Keyboard.', 1099.99, 'ipad_pro.jpg'),
        ('Bose QuietComfort Ultra', 'Premium noise-cancelling earbuds with immersive audio, CustomTune technology, and up to 6 hours of battery life. Weather-resistant design for all-day comfort.', 299.95, 'bose_earbuds.jpg'),
        ('Dell XPS 15', 'Premium Windows laptop with InfinityEdge display, 13th Gen Intel Core processors, NVIDIA GeForce RTX graphics, and CNC machined aluminum chassis.', 1899.99, 'dell_xps15.jpg'),
        ('DJI Mini 3 Pro', 'Lightweight sub-249g drone with 4K/60fps video, 48MP photos, and 34-minute flight time. Features obstacle sensing and advanced autonomous flying modes.', 759.00, 'dji_mini3.jpg')
    ],
    'clothing': [
        ('Nike Air Force 1 \'07', 'Iconic white leather sneakers that deliver lasting comfort and timeless style. Features durable construction, padded collar, and classic design.', 110.00, 'nike_af1.jpg'),
        ('Levi\'s 501 Original Fit Jeans', 'The original blue jean since 1873. Straight leg, button fly, and signature Levi\'s leather patch. 100% cotton denim with vintage-inspired finish.', 69.50, 'levis_501.jpg'),
        ('Patagonia Nano Puff Jacket', 'Lightweight, windproof, and water-resistant insulated jacket. Made with 100% recycled polyester and PrimaLoft Gold Insulation. Perfect for layering in unpredictable weather.', 229.00, 'patagonia_nano.jpg'),
        ('Ralph Lauren Classic Fit Polo', 'Timeless polo shirt crafted from soft cotton mesh. Features the iconic pony embroidery, ribbed collar, and two-button placket.', 98.50, 'polo_shirt.jpg'),
        ('The North Face ThermoBall Eco Jacket', 'Packable insulated jacket with innovative ThermoBall Eco technology. Water-resistant, lightweight, and made from recycled materials.', 230.00, 'northface_jacket.jpg'),
        ('Adidas Ultraboost 24', 'Premium running shoes with responsive Boost midsole, Primeknit+ upper, and Continental rubber outsole. Offers superior comfort and energy return with each stride.', 190.00, 'adidas_ultraboost.jpg')
    ],
    'home': [
        ('Dyson V15 Detect Absolute', 'Intelligent cordless vacuum with laser dust detection, piezo sensor, and 60-minute run time. Features HEPA filtration and specialized cleaner heads for different surfaces.', 799.99, 'dyson_v15.jpg'),
        ('Ninja Foodi 14-in-1 Smart XL Pressure Cooker', 'Multi-cooker with TenderCrisp technology, SmartLid, and 14 cooking functions. Pressure cook, air fry, steam, slow cook, and more in one device.', 349.95, 'ninja_foodi.jpg'),
        ('Le Creuset Signature Round Dutch Oven', 'Versatile enameled cast iron cookware with superior heat distribution and retention. Ideal for slow cooking, roasting, baking, and more.', 420.00, 'le_creuset.jpg'),
        ('Vitamix A3500 Ascent Series Blender', 'Professional-grade blender with five program settings, variable speed control, and digital timer. Features self-detect technology and wireless connectivity.', 649.95, 'vitamix_blender.jpg'),
        ('Philips Hue White and Color Ambiance Starter Kit', 'Smart lighting system with three color bulbs, bridge, and dimmer switch. Control via app or voice with 16 million colors and warm-to-cool white light.', 199.99, 'philips_hue.jpg'),
        ('Bose Smart Soundbar 900', 'Premium soundbar with Dolby Atmos, Voice4Video technology, and built-in voice assistants. Features Bose spatial technologies for immersive sound.', 899.00, 'bose_soundbar.jpg')
    ],
    'books': [
        ('Fourth Wing', 'Rebecca Yarros - Enter the brutal world of dragon riders at Basgiath War College, where survival is just the beginning.', 19.99, 'fourth_wing.jpg'),
        ('Iron Flame', 'Rebecca Yarros - Sequel to Fourth Wing, continuing the epic fantasy saga of dragons and warfare.', 22.99, 'iron_flame.jpg'),
        ('Atomic Habits', 'James Clear - Proven framework for improving every day through tiny changes that lead to remarkable results.', 16.99, 'atomic_habits.jpg'),
        ('The Housemaid', 'Freida McFadden - Psychological thriller about a housemaid who discovers her perfect employers are hiding deadly secrets.', 10.99, 'housemaid.jpg'),
        ('Dune', 'Frank Herbert - Science fiction masterpiece that inspired generations with its complex world-building and political intrigue.', 19.99, 'dune_book.jpg'),
        ('The 48 Laws of Power', 'Robert Greene - Amoral, candid, and instructive guide distilled from 3,000 years of history about obtaining, defending, and exercising power.', 25.00, '48_laws.jpg')
    ],
    'toys': [
        ('LEGO Star Wars Ultimate Millennium Falcon', 'Most detailed LEGO Star Wars Millennium Falcon ever created, featuring 7,541 pieces, detailed interior, and authentic features from the films.', 849.99, 'lego_falcon.jpg'),
        ('Nintendo Switch OLED Model', 'Enhanced gaming system with 7" OLED screen, wide adjustable stand, enhanced audio, and 64GB internal storage.', 349.99, 'switch_oled.jpg'),
        ('Barbie Dreamhouse 2023', 'Three-story, 8-room doll house with working elevator, pool, slide, and over 75 pieces including furniture and accessories.', 229.00, 'barbie_dreamhouse.jpg'),
        ('PlayStation 5 Digital Edition', 'Next-generation gaming console featuring lightning-fast loading, haptic feedback, adaptive triggers, and immersive 3D audio.', 399.99, 'ps5_digital.jpg'),
        ('Magic Mixies Magical Crystal Ball', 'Interactive toy that creates real mist as children cast spells to reveal their fortune-telling pet. Features over 80 sounds and reactions.', 84.99, 'magic_mixies.jpg'),
        ('Pokémon Trading Card Game: Scarlet & Violet Elite Trainer Box', 'Premium collection featuring 9 booster packs, card sleeves, energy cards, and accessories for competitive play.', 49.99, 'pokemon_etb.jpg')
    ],
    'sports': [
        ('YETI Tundra 45 Cooler', 'Virtually indestructible rotomolded cooler that keeps ice for days. Features T-Rex lid latches, NeverFail hinge system, and PermaFrost insulation.', 325.00, 'yeti_tundra.jpg'),
        ('Peloton Bike+', 'Premium connected fitness bike with 24" rotating HD touchscreen, automatic resistance, and integration with the Peloton App.', 2495.00, 'peloton_bike.jpg'),
        ('Titleist Pro V1 Golf Balls', 'Tour-proven golf balls offering exceptional distance, consistent flight, Drop-and-Stop control, and very soft feel.', 54.99, 'titleist_balls.jpg'),
        ('Osprey Atmos AG 65 Backpack', 'Award-winning backpacking pack with Anti-Gravity suspension, adjustable harness, and integrated raincover.', 340.00, 'osprey_pack.jpg'),
        ('Garmin Forerunner 955 Solar', 'Advanced GPS running smartwatch with solar charging, detailed training metrics, and full-color maps.', 599.99, 'garmin_watch.jpg'),
        ('Hydro Flask Wide Mouth 32oz', 'Double-wall vacuum insulated water bottle that keeps beverages cold for 24 hours or hot for 12 hours.', 44.95, 'hydroflask.jpg')
    ],
    'jewelry': [
        ('Pandora Moments Heart Clasp Snake Chain Bracelet', 'Sterling silver bracelet featuring heart-shaped clasp and compatible with all Pandora charms.', 75.00, 'pandora_bracelet.jpg'),
        ('Tiffany & Co. Elsa Peretti Open Heart Pendant', 'Iconic sterling silver heart pendant on 16" chain, celebrating Elsa Peretti\'s organic, sensual style.', 200.00, 'tiffany_heart.jpg'),
        ('Citizen Eco-Drive Promaster Diver', 'Professional dive watch powered by any light source with 200m water resistance and anti-reflective crystal.', 395.00, 'citizen_watch.jpg'),
        ('Swarovski Symbolic Evil Eye Pendant', 'Blue crystal pendant featuring the protective evil eye symbol on a rhodium-plated chain.', 125.00, 'swarovski_pendant.jpg'),
        ('Michael Kors Runway Chronograph Watch', 'Stainless steel chronograph watch featuring three-link bracelet, date display, and stopwatch functionality.', 250.00, 'mk_watch.jpg'),
        ('David Yurman Cable Classic Bracelet', 'Iconic twisted cable bracelet with 14k gold end caps and sterling silver construction.', 395.00, 'david_yurman.jpg')
    ]
}

# Real user first and last names for better data
CUSTOMER_NAMES = [
    ("Emma", "Thompson"),
    ("Michael", "Rodriguez"),
    ("Sarah", "Chen"),
    ("David", "Patel"),
    ("Olivia", "Johnson"),
    ("James", "Wong"),
    ("Sophia", "Miller"),
    ("Ethan", "Garcia")
]

# Real vendor business names
VENDOR_BUSINESSES = [
    ("TechWorld Electronics", "electronics"),
    ("Urban Style Clothing", "clothing"),
    ("Homey Essentials", "home"),
    ("BookWorm Paradise", "books"),
    ("PlayTime Toys", "toys"),
    ("ActiveLife Sports", "sports"),
    ("Sparkle Jewelry", "jewelry"),
    ("Gadgets & Gizmos", "electronics")
]

def clean_email_domain(name):
    """Clean up a string to be a valid domain-like name"""
    # Remove apostrophes and non-word characters
    name = re.sub(r"[^\w]", "", name)
    # Lowercase everything
    return name.lower()

class Command(BaseCommand):
    help = 'Populate database with realistic e-commerce data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset the database before populating',
        )

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating realistic e-commerce data...")
        
        if kwargs['reset']:
            self.reset_database()
        
        # Define placeholder image locations
        self.profile_images = self.get_image_files('profile_images')
        self.item_images = self.get_image_files('items')
        self.used_item_images = self.get_image_files('used-items')
        
        try:
            # Create users in separate transactions
            admin = self.create_admin()
            delivery_user = self.create_delivery_personnel()
            customers = self.create_customers(4)
            vendors = self.create_vendors(4)
            
            all_users = customers + vendors + [delivery_user] + [admin]
            
            # Create addresses and wallets in batches
            self.create_addresses_for_users(all_users)
            self.create_wallets_for_users(all_users)
            
            # Create items and used items
            items = self.create_items_for_vendors(vendors)
            used_items = self.create_used_items_for_customers(customers)
            
            # Create inventory for items
            self.create_inventory_for_items(items)
            
            # Create orders, transactions, and related data
            orders = self.create_orders_for_customers(customers, items)
            self.create_transactions_for_orders(orders)
            
            # Create additional entities
            discounts = self.create_discounts_for_vendors(vendors)
            self.create_carts_for_customers(customers, items, discounts)
            self.create_bids_for_customers(customers, used_items)
            self.create_notifications_for_users(all_users)
            self.create_ratings_for_items(customers, items)
            
            self.stdout.write(self.style.SUCCESS('Successfully populated database with realistic e-commerce data!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
            raise

    def reset_database(self):
        """Reset the database by deleting all records"""
        self.stdout.write("Resetting database...")
        
        models = [
            Rating, Notification, Bid, Cart, Discount, 
            Transaction, OrderItem, Order, Inventory, 
            UsedItem, Item, Wallet, Address, User
        ]
        
        for model in models:
            try:
                count = model.objects.all().count()
                model.objects.all().delete()
                self.stdout.write(f"Deleted {count} {model.__name__} records")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error deleting {model.__name__}: {e}"))

    def get_image_files(self, folder_name):
        """Get a list of image files from a folder"""
        media_dir = os.path.join(settings.MEDIA_ROOT, folder_name)
        
        # Create directory if it doesn't exist
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
            self.stdout.write(f"Created directory: {media_dir}")
            return []
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        return [
            os.path.join(folder_name, f) for f in os.listdir(media_dir) 
            if os.path.isfile(os.path.join(media_dir, f)) and 
            any(f.lower().endswith(ext) for ext in image_extensions)
        ]

    def get_random_image(self, category):
        """Get a random image path based on category"""
        if category == 'profile':
            return random.choice(self.profile_images) if self.profile_images else None
        elif category == 'item':
            return random.choice(self.item_images) if self.item_images else None
        elif category == 'used_item':
            return random.choice(self.used_item_images) if self.used_item_images else None
        return None

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
                    verification_status='verified',
                    profile_image=self.get_random_image('profile')
                )
                return admin
        except IntegrityError:
            self.stdout.write(self.style.WARNING(f'Admin user already exists'))
            return User.objects.get(username='admin')

    def create_delivery_personnel(self):
        try:
            with transaction.atomic():
                first_name = "Alex"
                last_name = "Delivery"
                username = "delivery_alex"
                self.stdout.write(f"Creating delivery person: {username}")
                
                user = User.objects.create_user(
                    username=username,
                    email='delivery.alex@marketplace.com',
                    phone='+18005552345',
                    first_name=first_name,
                    last_name=last_name,
                    user_type='delivery',
                    password='delivery123',
                    verification_status='verified',
                    business_name="Alex's Swift Delivery",
                    profile_image=self.get_random_image('profile')
                )
                return user
        except IntegrityError:
            self.stdout.write(self.style.WARNING(f'Delivery user already exists'))
            return User.objects.get(username='delivery_alex')

    def create_customers(self, count):
        customers = []
        
        # Use predefined names
        customer_data = CUSTOMER_NAMES[:count]
        
        for i, (first_name, last_name) in enumerate(customer_data):
            try:
                with transaction.atomic():
                    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
                    username = f"{first_name.lower()}{random.randint(100, 999)}"
                    
                    self.stdout.write(f"Creating customer {i+1}/{count}: {first_name} {last_name}")
                    
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        phone=f"+1{random.randint(2000000000, 9999999999)}",
                        first_name=first_name,
                        last_name=last_name,
                        user_type='customer',
                        password='customer123',
                        verification_status='verified',
                        profile_image=self.get_random_image('profile')
                    )
                    customers.append(user)
            except IntegrityError:
                self.stdout.write(self.style.WARNING(f'Customer {username} already exists'))
                continue
        
        return customers

    def create_vendors(self, count):
        vendors = []
        
        # Use predefined vendor businesses
        vendor_data = VENDOR_BUSINESSES[:count]
        
        for i, (business_name, primary_category) in enumerate(vendor_data):
            try:
                with transaction.atomic():
                    clean_business = clean_email_domain(business_name)
                    username = f"{clean_business}"
                    
                    self.stdout.write(f"Creating vendor {i+1}/{count}: {business_name}")
                    
                    user = User.objects.create_user(
                        username=username,
                        email=f"contact@{clean_business}.com",
                        phone=f"+1{random.randint(2000000000, 9999999999)}",
                        first_name="",  # Business vendors don't need first/last name
                        last_name="",
                        user_type='vendor',
                        business_name=business_name,
                        password='vendor123',
                        verification_status='verified',
                        vendor_type='business',
                        business_license=f"BL{random.randint(100000, 999999)}",
                        rating=Decimal(random.uniform(4.0, 5.0)).quantize(Decimal('0.1')),
                        profile_image=self.get_random_image('profile')
                    )
                    # Store primary category for later use when creating items
                    user.primary_category = primary_category
                    vendors.append(user)
            except IntegrityError:
                self.stdout.write(self.style.WARNING(f'Vendor {username} already exists'))
                continue
        
        return vendors

    def create_wallets_for_users(self, users):
        """Create a wallet for each user"""
        self.stdout.write("Creating wallets for users...")
        
        for user in users:
            try:
                with transaction.atomic():
                    # Create more realistic blockchain-like address
                    wallet_address = f"0x{uuid.uuid4().hex[:40]}"
                    
                    # Balance depends on user type
                    if user.user_type == 'customer':
                        balance = Decimal(random.uniform(100, 2000)).quantize(Decimal('0.01'))
                    elif user.user_type == 'vendor':
                        balance = Decimal(random.uniform(5000, 50000)).quantize(Decimal('0.01'))
                    else:
                        balance = Decimal(random.uniform(1000, 5000)).quantize(Decimal('0.01'))
                    
                    Wallet.objects.create(
                        address=wallet_address,
                        balance=balance,
                        user=user
                    )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating wallet for {user.username}: {e}'))

    def create_items_for_vendors(self, vendors):
        """Create items for each vendor based on their primary category"""
        all_items = []
        self.stdout.write("Creating items for vendors...")
        
        for vendor in vendors:
            try:
                with transaction.atomic():
                    # Get the vendor's primary category, fallback to a random one if not set
                    primary_category = getattr(vendor, 'primary_category', random.choice(list(PRODUCTS.keys())))
                    
                    # Get products for this category
                    category_products = PRODUCTS[primary_category]
                    
                    # Create 5-8 items for this vendor
                    num_items = random.randint(5, 8)
                    selected_products = random.sample(category_products, min(num_items, len(category_products)))
                    
                    for name, description, price, image_name in selected_products:
                        item = Item.objects.create(
                            name=name,
                            description=description,
                            price=Decimal(price),
                            category=primary_category,
                            vendor=vendor,
                            image=self.get_random_image('item')
                        )
                        self.stdout.write(f"Created item: {item.name} for {vendor.business_name}")
                        all_items.append(item)
                    
                    # Add 1-2 items from other random categories for variety
                    other_categories = [k for k in PRODUCTS.keys() if k != primary_category]
                    if other_categories:
                        random_category = random.choice(other_categories)
                        random_products = random.sample(PRODUCTS[random_category], min(2, len(PRODUCTS[random_category])))
                        
                        for name, description, price, image_name in random_products:
                            item = Item.objects.create(
                                name=name,
                                description=description,
                                price=Decimal(price),
                                category=random_category,
                                vendor=vendor,
                                image=self.get_random_image('item')
                            )
                            self.stdout.write(f"Created item: {item.name} for {vendor.business_name}")
                            all_items.append(item)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating items for {vendor.business_name}: {e}'))
        
        return all_items

    def create_inventory_for_items(self, items):
        """Create inventory records for all items"""
        self.stdout.write("Creating inventory for items...")
        
        for item in items:
            try:
                with transaction.atomic():
                    # Most items are in stock
                    in_stock = random.random() < 0.9
                    
                    # Quantity between 5-100 for in-stock items
                    quantity = random.randint(5, 100) if in_stock else 0
                    
                    # Random warehouse location
                    location = random.choice([
                        'East Coast Warehouse', 
                        'West Coast Distribution Center',
                        'Central Fulfillment Center',
                        'Main Retail Store',
                        'Supplier Direct'
                    ])
                    
                    # Last restocked between 1-60 days ago
                    restock_date = now() - timedelta(days=random.randint(1, 60))
                    
                    Inventory.objects.create(
                        item=item,
                        item_quantity=quantity,
                        in_stock=in_stock,
                        location=location,
                        last_restocked=restock_date
                    )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating inventory for {item.name}: {e}'))

    def create_used_items_for_customers(self, customers):
        """Create used items for each customer"""
        all_used_items = []
        self.stdout.write("Creating used items for customers...")
        
        for customer in customers:
            try:
                with transaction.atomic():
                    # Each customer has 2-3 used items
                    num_items = random.randint(2, 3)
                    
                    # Create used items across different categories
                    categories = random.sample(list(PRODUCTS.keys()), min(num_items, len(PRODUCTS.keys())))
                    
                    for category in categories:
                        # Select a random product from this category
                        name, description, price, _ = random.choice(PRODUCTS[category])
                        
                        # Used items are 40-80% of original price
                        used_price = Decimal(price * random.uniform(0.4, 0.8)).quantize(Decimal('0.01'))
                        
                        # Create used item
                        used_item = UsedItem.objects.create(
                            name=f"Used {name}",
                            description=f"Pre-owned {description} in {random.choice(['excellent', 'good', 'fair'])} condition. {random.choice(['Light scratches', 'Like new', 'Minor wear', 'Well maintained'])}. {random.choice(['Original box included', 'All accessories included', 'Comes with case', 'Recently serviced'])}.",
                            price=used_price,
                            category=category,
                            warranty_period=random.randint(0, 6),  # 0-6 months warranty
                            user=customer,
                            image=self.get_random_image('used_item')
                        )
                        
                        self.stdout.write(f"Created used item: {used_item.name} by {customer.first_name}")
                        all_used_items.append(used_item)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating used items for {customer.first_name}: {e}'))
        
        return all_used_items

    def create_orders_for_customers(self, customers, items):
        """Create orders for each customer"""
        all_orders = []
        self.stdout.write("Creating orders for customers...")
        
        for customer in customers:
            try:
                with transaction.atomic():
                    # Each customer has 2-4 orders
                    num_orders = random.randint(2, 4)
                    
                    for _ in range(num_orders):
                        # Determine order status with weighted probabilities
                        status = random.choices(
                            ['pending', 'shipped', 'delivered', 'cancelled'],
                            weights=[0.2, 0.3, 0.4, 0.1],
                            k=1
                        )[0]
                        
                        order_date = now() - timedelta(days=random.randint(1, 60))
                        
                        # Create the order
                        order = Order.objects.create(
                            user=customer,
                            status=status,
                            created_at=order_date,
                            updated_at=order_date + timedelta(days=random.randint(1, 5)) if status != 'pending' else order_date
                        )
                        
                        # Add 1-4 items to the order
                        num_items = random.randint(1, 4)
                        selected_items = random.sample(items, num_items)
                        
                        total_amount = Decimal('0.00')
                        
                        for item in selected_items:
                            quantity = random.randint(1, 3)
                            
                            OrderItem.objects.create(
                                order=order,
                                item=item,
                                quantity=quantity,
                                price_at_purchase=item.price  # Changed from 'price' to 'price_at_purchase'
                            )
                            
                            total_amount += item.price * quantity
                        
                        # Update order total
                        order.total_amount = total_amount
                        order.save()
                        
                        self.stdout.write(f"Created order #{order.id} for {customer.first_name} with {num_items} items")
                        all_orders.append(order)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating orders for {customer.first_name}: {e}'))
        
        return all_orders

    def create_addresses_for_users(self, users):
        self.stdout.write("Creating addresses for users...")
        
        address_types = ["Home", "Work"]
        
        for user in users:
            for address_type in address_types:
                try:
                    with transaction.atomic():
                        state = random.choice([
                            'CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'
                        ])
                        
                        city = random.choice([
                            'Los Angeles', 'New York', 'Chicago', 'Houston', 'Phoenix',
                            'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'Austin'
                        ])
                        
                        Address.objects.create(
                            street_address=f"{random.randint(100, 9999)} {random.choice(['Main', 'Park', 'Oak', 'Pine', 'Maple'])} {random.choice(['St', 'Ave', 'Blvd', 'Rd', 'Ln'])}",
                            city=city,
                            state=state,
                            postal_code=f"{random.randint(10000, 99999)}",
                            country='USA',
                            user=user
                        )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error creating address for {user.username}: {e}'))

    def create_discounts_for_vendors(self, vendors):
        """Create discounts for each vendor"""
        all_discounts = []
        self.stdout.write("Creating discounts for vendors...")
        
        for vendor in vendors:
            try:
                with transaction.atomic():
                    # Each vendor has 2-4 discounts
                    num_discounts = random.randint(2, 4)
                    
                    for i in range(num_discounts):
                        # Create discount code
                        code = f"{vendor.business_name[:3].upper()}{random.randint(100, 999)}"
                        
                        # Create discount
                        discount = Discount.objects.create(
                            code=code,
                            name=f"{vendor.business_name} Discount {i+1}",
                            percentage=Decimal(random.uniform(5, 30)).quantize(Decimal('0.1')),
                            expires_at=now() + timedelta(days=random.randint(30, 90)),
                            max_redemptions=random.randint(50, 200),
                            vendor=vendor
                        )
                        
                        self.stdout.write(f"Created discount: {code} for {vendor.business_name}")
                        all_discounts.append(discount)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating discounts for {vendor.business_name}: {e}'))
        
        return all_discounts

    def create_carts_for_customers(self, customers, items, discounts):
        """Create cart items for each customer"""
        self.stdout.write("Creating cart items for customers...")
        
        for customer in customers:
            try:
                with transaction.atomic():
                    # Each customer has 1-3 items in cart
                    num_items = random.randint(1, 3)
                    selected_items = random.sample(items, num_items)
                    
                    for item in selected_items:
                        # 30% chance of having a discount applied
                        apply_discount = random.random() < 0.3
                        discount = random.choice(discounts) if apply_discount and discounts else None
                        
                        Cart.objects.create(
                            user=customer,
                            item=item,
                            item_quantity=random.randint(1, 3),
                            discount=discount
                        )
                    
                    self.stdout.write(f"Created cart with {num_items} items for {customer.first_name}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating cart for {customer.first_name}: {e}'))

    def create_bids_for_customers(self, customers, used_items):
        """Create bids on used items (not their own)"""
        self.stdout.write("Creating bids for customers...")
        
        for customer in customers:
            try:
                with transaction.atomic():
                    # Each customer makes 1-3 bids on items not their own
                    num_bids = random.randint(1, 3)
                    
                    # Get used items not belonging to this customer
                    available_items = [ui for ui in used_items if ui.user != customer]
                    
                    if not available_items:
                        continue
                    
                    selected_items = random.sample(available_items, min(num_bids, len(available_items)))
                    
                    for item in selected_items:
                        # Convert item price to Decimal if it isn't already
                        item_price = Decimal(str(item.price))
                        
                        # Bid between 70-120% of asking price
                        bid_amount = (item_price * Decimal(random.uniform(0.7, 1.2))).quantize(Decimal('0.01'))
                        
                        Bid.objects.create(
                            user=customer,
                            used_item=item,
                            amount=bid_amount,
                            status='bidding'
                        )
                    
                    self.stdout.write(f"Created {num_bids} bids for {customer.first_name}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating bids for {customer.first_name}: {e}'))

    def create_notifications_for_users(self, users):
        """Create notifications for all users"""
        self.stdout.write("Creating notifications for users...")
        
        notification_types = [
            ('system', 'System maintenance scheduled for tomorrow at 2 AM'),
            ('general', 'Welcome to our marketplace! Start shopping now'),
            ('product', 'New items added to your favorite category'),
            ('general', 'Your order has been shipped'),
            ('product', 'Special discount on items you viewed'),
            ('system', 'Your account has been verified')
        ]
        
        for user in users:
            try:
                with transaction.atomic():
                    # Each user gets 3-8 notifications
                    num_notifications = random.randint(3, 8)
                    
                    for _ in range(num_notifications):
                        # Select random notification type and text
                        notification_type, text = random.choice(notification_types)
                        
                        # 70% chance of being read
                        is_read = random.random() < 0.7
                        
                        Notification.objects.create(
                            user=user,
                            type=notification_type,
                            text=text,
                            read=is_read
                        )
                    
                    self.stdout.write(f"Created {num_notifications} notifications for {user.username}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating notifications for {user.username}: {e}'))

    def create_ratings_for_items(self, customers, items):
        """Create ratings for items"""
        self.stdout.write("Creating ratings for items...")
        
        for item in items:
            try:
                with transaction.atomic():
                    # Each item gets 3-10 ratings
                    num_ratings = random.randint(3, 10)
                    selected_customers = random.sample(customers, min(num_ratings, len(customers)))
                    
                    for customer in selected_customers:
                        # Rating between 3-5 stars (weighted towards higher ratings)
                        rating_value = random.choices(
                            [3, 4, 5],
                            weights=[0.2, 0.3, 0.5],
                            k=1
                        )[0]
                        
                        Rating.objects.create(
                            user=customer,
                            item=item,
                            rating=rating_value,
                            review=random.choice([
                                "Great product, would buy again!",
                                "Exactly as described",
                                "Fast shipping, good quality",
                                "Met my expectations",
                                "Good value for the price",
                                "Highly recommend",
                                "Works perfectly",
                                "Better than expected"
                            ])
                        )
                    
                    self.stdout.write(f"Created ratings for {item.name}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating ratings for {item.name}: {e}'))
                
    def create_transactions_for_orders(self, orders):
        """Create transactions for each order"""
        self.stdout.write("Creating transactions for orders...")
        
        for order in orders:
            try:
                with transaction.atomic():
                    # Skip cancelled orders
                    if order.status == 'cancelled':
                        continue
                    
                    # Get the customer's wallet
                    wallet = order.user.user_wallet.first()
                    if not wallet:
                        self.stdout.write(self.style.WARNING(f'No wallet found for user {order.user.username}'))
                        continue
                    
                    # Create transaction with unique hash
                    transaction_hash = f"tx_{uuid.uuid4().hex[:20]}"
                    transaction_obj = Transaction.objects.create(
                        transaction_hash=transaction_hash,
                        status='completed',
                        order=order,
                        user=order.user,
                        created_at=order.created_at,
                        updated_at=order.created_at
                    )
                    
                    # Update wallet balance
                    wallet.balance -= order.total_amount
                    wallet.save()
                    
                    self.stdout.write(f"Created transaction {transaction_hash} for order #{order.id}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating transaction for order #{order.id}: {e}'))