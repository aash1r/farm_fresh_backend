#!/usr/bin/env python3
"""
Database Seeder Script
Run with: python seed_db.py
"""


## run this command in project root directory to seed the database
# python -m app.db.seeder

import random
import sys
from faker import Faker
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus, DeliveryType
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
fake = Faker()

MANGO_TYPES = ["Sindhri", "Langra", "Chaunsa", "Ratol"]
CITIES = ["Karachi", "Lahore", "Islamabad", "Faisalabad", "Rawalpindi", "Multan", "Peshawar", "Quetta"]
STATES = ["Sindh", "Punjab", "KPK", "Balochistan", "Gilgit-Baltistan"]
VARIATIONS = ["Pack of 3", "Pack of 6", "Pack of 8", "Pack of 12", "Box of 24"]
ORDER_NOTES = [
    "Please call before delivery",
    "Leave at gate if no one home", 
    "Handle with care - gift order",
    "Fragile - contains ripe mangoes",
    "Call 30 minutes before arrival"
]
AIRPORTS = {
    "KHI": "Jinnah International Airport",
    "LHE": "Allama Iqbal International Airport", 
    "ISB": "Islamabad International Airport"
}

def clear_database(db: Session):
    """Clear all existing data"""
    print("🗑️  Clearing existing data...")
    
    db.query(OrderItem).delete()
    db.query(Order).delete() 
    db.query(Product).delete()
    db.query(User).delete()
    
    db.commit()
    print("✅ Database cleared!")

def create_users(db: Session, count: int = 20):
    """Create test users"""
    print(f"👥 Creating {count} users...")
    
    users = []
    
    for i in range(2):
        user = User(
            email=f"admin{i+1}@farmfresh.com",
            username=f"admin{i+1}",
            hashed_password="$2b$12$dummy.hash.for.testing.purposes.only",
            address=f"{random.choice(CITIES)}, {fake.street_address()}",
            is_admin=True,
            is_verified=True
        )
        users.append(user)
    
    # Create regular users
    for i in range(count - 2):
        user = User(
            email=f"user{i+1}@example.com",
            username=f"user{i+1}",
            hashed_password="$2b$12$dummy.hash.for.testing.purposes.only",
            address=f"{random.choice(CITIES)}, {fake.street_address()}",
            is_admin=False,
            is_verified=random.choice([True, False])
        )
        users.append(user)
    
    db.add_all(users)
    db.commit()
    
    print(f"✅ Created {len(users)} users (2 admins, {len(users)-2} regular users)")
    return users

def create_products(db: Session, count: int = 30):
    """Create test products"""
    print(f"🥭 Creating {count} products...")
    
    products = []
    
    for i in range(count):
        mango_type = random.choice(MANGO_TYPES)
        variation = random.choice(VARIATIONS)
        
        # Generate realistic prices based on variation
        base_price = random.uniform(800, 2500)
        if "Box" in variation:
            base_price *= 1.5
        elif "Pack of 12" in variation:
            base_price *= 1.2
            
        product = Product(
            name=f"{mango_type} Mangoes",
            description=f"Fresh {mango_type} mangoes directly from Pakistani farms. "
                       f"Known for their {random.choice(['sweet', 'juicy', 'aromatic', 'rich'])} flavor. "
                       f"Perfect for {random.choice(['families', 'gifting', 'special occasions', 'daily consumption'])}.",
            price=round(base_price, 2),
            image_url=f"https://farmfresh.com/images/{mango_type.lower()}{i+1}.jpg",
            type=mango_type,
            variation_name=variation,
            stock=random.randint(10, 100)
        )
        products.append(product)
    
    db.add_all(products)
    db.commit()
    
    print(f"✅ Created {len(products)} products")
    return products

def create_orders(db: Session, users: list, products: list, count: int = 50):
    """Create test orders with order items"""
    print(f"📦 Creating {count} orders...")
    
    orders = []
    order_items = []
    
    for i in range(count):
        user = random.choice(users)
        delivery_type = random.choice([DeliveryType.PICKUP, DeliveryType.DOORSTEP])
        status = random.choice([OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
        
        # Generate Pakistani phone number
        phone = f"+923{random.randint(100000000, 999999999)}"
        
        # Choose airport for pickup
        airport_code = random.choice(list(AIRPORTS.keys()))
        
        order = Order(
            order_number=f"ORD-{str(i+1).zfill(6)}",
            total_amount=0,  # Will calculate after adding items
            status=status,
            delivery_type=delivery_type,
            is_mango_delivery=True,
            shipping_zip=str(random.randint(10000, 99999)),
            shipping_address=f"House # {random.randint(1, 999)}, {fake.street_name()}",
            shipping_city=random.choice(CITIES),
            shipping_state=random.choice(STATES),
            country="Pakistan",
            whatsapp_number=phone,
            email_address=f"customer{i+1}@example.com",
            order_notes=random.choice(ORDER_NOTES) if random.random() < 0.7 else None,
            airport_code=airport_code,
            airport_name=AIRPORTS[airport_code],
            payment_id=f"PAY-{str(i+1).zfill(8)}",
            user_id=user.id
        )
        
        db.add(order)
        db.flush()  # Get the order ID
        
        # Add 1-4 items per order
        order_total = 0
        num_items = random.randint(1, 4)
        selected_products = random.sample(products, num_items)
        
        for product in selected_products:
            quantity = random.randint(1, 5)
            # Add some price variation (±20%)
            unit_price = product.price * random.uniform(0.8, 1.2)
            total_price = quantity * unit_price
            order_total += total_price
            
            order_item = OrderItem(
                quantity=quantity,
                unit_price=round(unit_price, 2),
                total_price=round(total_price, 2),
                mango_type=random.choice(MANGO_TYPES),
                variation_name=random.choice(VARIATIONS),
                order_id=order.id,
                product_id=product.id
            )
            order_items.append(order_item)
        
        # Update order total
        order.total_amount = round(order_total, 2)
        orders.append(order)
    
    # Add all order items
    db.add_all(order_items)
    db.commit()
    
    print(f"✅ Created {len(orders)} orders with {len(order_items)} order items")
    return orders, order_items

def seed_database():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Clear existing data
        clear_database(db)
        
        # Create test data
        users = create_users(db, count=20)
        products = create_products(db, count=30) 
        orders, order_items = create_orders(db, users, products, count=50)
        
        print("\n" + "=" * 50)
        print("🎉 Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   • Users: {len(users)} (2 admins, {len(users)-2} regular)")
        print(f"   • Products: {len(products)}")
        print(f"   • Orders: {len(orders)}")
        print(f"   • Order Items: {len(order_items)}")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Farm Fresh Shop - Database Seeder")
    print("This will clear all existing data and create test data.")
    
    # Uncomment the line below to require confirmation
    # confirm = input("Are you sure you want to proceed? (yes/no): ")
    # if confirm.lower() != 'yes':
    #     print("Seeding cancelled.")
    #     sys.exit(0)
    
    try:
        seed_database()
    except KeyboardInterrupt:
        print("\n❌ Seeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)