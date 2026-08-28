import pytest
from app import create_app
from configuration.extensions import db as _db
from model.models import Product, Category, User, Order
from datetime import datetime

@pytest.fixture(scope='module')
def app():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }
    flask_app = create_app(test_config)

    with flask_app.app_context():
        _db.create_all()

        category = Category(name='Electronics', is_active=True, created_at=datetime.now())
        _db.session.add(category)
        _db.session.flush()

        product1 = Product(name='Laptop Gaming', price=2999.99, stock_quantity=1, category_id=category.id, created_at=datetime.now())
        product2 = Product(name='Webcam', price=99.99, stock_quantity=2, category_id=category.id, created_at=datetime.now())
        _db.session.add_all([product1, product2])
        
        user = User(username='John', email='johntest123@email.com', role='user', is_active=True, created_at=datetime.now())
        user.hashing_password('testpassword123')
        _db.session.add(user)
        _db.session.flush()

        order = Order(user_id=user.id, total_price=2999.99, status='pending', ordered_at=datetime.now())
        order.products = [product1]
        _db.session.add(order)
        _db.session.commit()

        yield flask_app
        
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()