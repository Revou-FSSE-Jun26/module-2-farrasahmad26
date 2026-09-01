import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from configuration.extensions import db
from model.models import Category, Product, User, Order

def seed_categories():
    categories = [
        Category(name='Electronics', description='Electronic devices'),
        Category(name='Books', description='Reading book'),
        Category(name='Clothing', description='Daily outfit')
    ]
    db.session.add_all(categories)
    db.session.commit()
    print(f"    categories: {len(categories)}")
    return categories

def seed_products(categories):
    cat = {c.name: c for c in categories}
    products = [
        Product(name='Wireless Mouse', category_id=cat['Electronics'].id, description='Mouse wireless', price=24.99, stock_quantity=150),
        Product(name='Mechanical Keyboard', category_id=cat['Electronics'].id, description='Keyboard gaming', price=99.99, stock_quantity=80),
        Product(name='Python Crash Course', category_id=cat['Books'].id, description='Python learning book', price=19.99, stock_quantity=50),
        Product(name='Cotton T-shirt', category_id=cat['Clothing'].id, description='Cotton combed T-shirt', price=9.99, stock_quantity=300),
    ]
    db.session.add_all(products)
    db.session.commit()
    print(f"    products: {len(products)}")
    return products

def seed_users():
    users_data = [
        {'username': 'admin', 'email': 'admin@email.com', 'role': 'admin'},
        {'username': 'Jhon Weak', 'email': 'jhon@email.com', 'role': 'user'},
        {'username': 'Andi Idna', 'email': 'andi@email.com', 'role': 'user'},
    ]
    users = []
    for data in users_data:
        user = User(username=data['username'], email=data['email'], role=data['role'])
        user.hashing_password('Password123')
        users.append(user)
    db.session.add_all(users)
    db.session.commit()
    print(f"    users: {len(users)}")
    return users

def seed_orders(users, products):
    orders_data = [
        {'user': users[1], 'products': products[0:2], 'status': 'paid'},
        {'user': users[2], 'products': products[2:4], 'status': 'pending'},
    ]
    created = 0
    for data in orders_data:
        prods = data['products']
        total = sum(p.price for p in prods)
        order = Order(user_id=data['user'].id, total_price=round(total, 2), status=data['status'])
        order.products = prods
        db.session.add(order)
        created += 1
    db.session.commit()
    print(f"    orders: {created} (automated order_items)")

def run_seed():
    print("initial seeding...")
    app = create_app()
    with app.app_context():
        categories = seed_categories()
        products = seed_products(categories)
        users = seed_users()
        seed_orders(users, products)
    print("Seeding done.")

if __name__ == '__main__':
    run_seed()