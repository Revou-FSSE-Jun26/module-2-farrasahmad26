# coding: utf-8
from datetime import datetime
from extensions import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.FetchedValue())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    def to_dict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'description' : self.description,
            'is_active' : self.is_active,
            'created_at' : self.created_at
        }

# class OrderItem(db.Model):
#     __tablename__ = 'order_items'
#     __table_args__ = (
#         db.CheckConstraint('quantity > 0'),
#     )

#     order_id = db.Column(db.ForeignKey('orders.id', ondelete='CASCADE'), primary_key=True, nullable=False)
#     product_id = db.Column(db.ForeignKey('products.id'), primary_key=True, nullable=False)
#     quantity = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())

#     order = db.relationship('Order', primaryjoin='OrderItem.order_id == Order.id', backref='order_items')
#     product = db.relationship('Product', primaryjoin='OrderItem.product_id == Product.id', backref='order_items')

#     def to_dict(self):
#         return {
#             'order_id' : self.order_id,
#             'product_id' : self.product_id,
#             'quantity' : self.quantity
#         }

order_items = db.Table('order_items',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = (
        db.CheckConstraint('total_price >= 0::numeric'),
    )

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    user_id = db.Column(db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    ordered_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    user = db.relationship('User', primaryjoin='Order.user_id == User.id', backref='orders')
    products = db.relationship('Product', secondary=order_items, backref='orders')

    def to_dict(self):
        return {
            'id' : self.id,
            'user_id' : self.user_id,
            'total_price' : self.total_price,
            'status' : self.status,
            'ordered_at' : self.ordered_at
        }

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    category = db.relationship('Category', primaryjoin='Product.category_id == Category.id', backref='products')

    def to_dict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'category_id' : self.category_id,
            'description' : self.description,
            'price' : self.price,
            'stock_quantity' : self.stock_quantity,
            'created_at' : self.created_at
        }

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, server_default="user")
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.FetchedValue())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    def to_dict(self):
        return {
            'id' : self.id,
            'username' : self.username,
            'email' : self.email,
            'role' : self.role,
            'is_active' : self.is_active,
            'created_at' : self.created_at
        }