# coding: utf-8
from datetime import datetime
from configuration.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    deleted_at = db.Column(db.DateTime, nullable=True)
    image = db.Column(db.Text)

    def active_product_count(self):
        return sum(1 for p in self.products if p.deleted_at is None)

    def to_dict(self, include_products=False):
        data = {
            'id' : self.id,
            'name' : self.name,
            'description' : self.description,
            # Soft-deleted categories are "inactive" (same rule as products).
            'is_active' : bool(self.is_active) and self.deleted_at is None,
            'created_at' : self.created_at,
            'deleted_at' : self.deleted_at,
            'image' : self.image,
            # Only active products count: that's what shoppers can see.
            'product_count' : self.active_product_count(),
        }
        if include_products:
            data['products'] = [p.to_dict() for p in self.products if p.deleted_at is None]
        return data

class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = (
        # Named to match the existing DB constraint so Alembic autogenerate stops trying to drop it.
        db.CheckConstraint('total_price >= 0', name='orders_total_price_check'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    ordered_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Checkout details. All nullable so orders created before checkout existed stay valid.
    # Card numbers / CVC / GoPay numbers are intentionally never stored.
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(150))
    address = db.Column(db.String(255))
    apartment = db.Column(db.String(255))
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    postal_code = db.Column(db.String(10))
    country = db.Column(db.String(100))
    shipping_method = db.Column(db.String(20))
    shipping_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0, server_default='0')
    payment_method = db.Column(db.String(20))
    note = db.Column(db.Text)

    user = db.relationship('User', primaryjoin='Order.user_id == User.id', backref='orders')

    def to_dict(self):
        return {
            'id' : self.id,
            'user_id' : self.user_id,
            'email' : self.user.email if self.user else None,
            'total_price' : float(self.total_price),
            'shipping_cost' : float(self.shipping_cost or 0),
            'status' : self.status,
            'ordered_at' : self.ordered_at,
            'first_name' : self.first_name,
            'last_name' : self.last_name,
            'phone' : self.phone,
            'company' : self.company,
            'address' : self.address,
            'apartment' : self.apartment,
            'city' : self.city,
            'province' : self.province,
            'postal_code' : self.postal_code,
            'country' : self.country,
            'shipping_method' : self.shipping_method,
            'payment_method' : self.payment_method,
            'note' : self.note,
            'items': [item.to_dict() for item in self.order_items]
        }

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    deleted_at = db.Column(db.DateTime, nullable=True)
    image = db.Column(db.Text)
    slug = db.Column(db.String(100), nullable=False, unique=True)

    category = db.relationship('Category', primaryjoin='Product.category_id == Category.id', backref='products')

    def to_dict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'category_id' : self.category_id,
            'category' : self.category.name if self.category else None,
            'description' : self.description,
            'price' : self.price,
            'stock_quantity' : self.stock_quantity,
            'created_at' : self.created_at,
            'image' : self.image,
            'slug' : self.slug,
            # Soft-deleted products are "inactive" in the admin dashboard.
            'is_active' : self.deleted_at is None,
            'deleted_at' : self.deleted_at,
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    __table_args__ = (
        db.CheckConstraint('quantity > 0'),
    )

    order_id = db.Column(db.ForeignKey('orders.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    product_id = db.Column(db.ForeignKey('products.id'), primary_key=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_order = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship('Order', backref='order_items')
    product = db.relationship('Product', backref='order_items')

    def to_dict(self):
        # Product info is included so the order pages don't need a second request.
        product = self.product
        return {
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price_at_order': float(self.price_at_order),
            'name': product.name if product else None,
            'slug': product.slug if product else None,
            'image': product.image if product else None,
            'category': product.category.name if product and product.category else None,
        }

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id' : self.id,
            'username' : self.username,
            'email' : self.email,
            'role' : self.role,
            'is_active' : self.is_active,
            'created_at' : self.created_at
        }
    
    def hashing_password(self, raw_pass):
        self.password_hash = generate_password_hash(raw_pass)
    
    def check_password(self, raw_pass):
        return check_password_hash(self.password_hash, raw_pass)

