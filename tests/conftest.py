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
        'JWT_SECRET_KEY': 'test-secret-key-that-is-long-enough-for-hs256',
    }
    flask_app = create_app(test_config)

    with flask_app.app_context():
        _db.create_all()

        category = Category(name='Electronics', is_active=True, created_at=datetime.now())
        _db.session.add(category)
        _db.session.flush()

        product1 = Product(name='Laptop Gaming', slug='laptop-gaming', price=2999.99, stock_quantity=1, category_id=category.id, created_at=datetime.now())
        product2 = Product(name='Webcam', slug='webcam', price=99.99, stock_quantity=2, category_id=category.id, created_at=datetime.now())
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


def _auth_headers(app, email, role):
    """Creates (or reuses) a user with the given role and returns Bearer headers for it."""
    from flask_jwt_extended import create_access_token
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(username=email.split('@')[0], email=email, role=role, is_active=True, created_at=datetime.now())
            user.hashing_password('password123')
            _db.session.add(user)
            _db.session.commit()
        token = create_access_token(identity=str(user.id), additional_claims={'email': user.email, 'role': user.role})
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='module')
def admin_headers(app):
    return _auth_headers(app, 'fixture-admin@email.com', 'admin')


@pytest.fixture(scope='module')
def user_headers(app):
    return _auth_headers(app, 'fixture-user@email.com', 'user')