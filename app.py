from flask import Flask, jsonify
from extensions import db
from models import Category, OrderItem, Order, Product, User
from routes import product_bp, user_bp, order_bp, order_item_bp, category_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/revoshop_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.register_blueprint(product_bp)
app.register_blueprint(user_bp)
app.register_blueprint(order_bp)
app.register_blueprint(order_item_bp)
app.register_blueprint(category_bp)

if __name__ == '__main__':
    app.run(debug=True)