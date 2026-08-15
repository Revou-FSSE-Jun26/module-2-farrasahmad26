from flask import jsonify, request, Blueprint
from extensions import db
from models import Category, order_items, Order, Product, User
from sqlalchemy.exc import IntegrityError

product_bp = Blueprint('products', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    if not products:
        return jsonify({'Error': 'No available product'}), 404
    return jsonify([product.to_dict() for product in products]), 200

@product_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data.get('name') or not data.get('category_id') or not data.get('price') or not data.get('stock_quantity'):
        return jsonify({'Error': 'name, category id, price, and stock quantity are required'}), 400

    product = Product(
        name=data.get('name'),
        category_id=data.get('category_id'),
        description=data.get('description'),
        price=data.get('price'),
        stock_quantity=data.get('stock_quantity')
    )
    try:
        db.session.add(product)
        db.session.commit()
        return jsonify(product.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'Error': 'Data violates database constraints'}), 409

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'Error': 'Product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'Message': 'Product deleted successfully'}), 200

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'Error': 'Product not found'}), 404
    return jsonify(product.to_dict()), 200

user_bp = Blueprint('users', __name__)

@user_bp.route('/users/register', methods=['POST'])
def register_user():
    data = request.get_json()

    if not data.get('username') or not data.get('email') or not data.get('password_hash'):
        return jsonify({'Error': 'username, email, and password are required'}), 400

    user = User(
        username=data.get('username'),
        email=data.get('email'),
        password_hash=data.get('password_hash')
    )
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'Error': 'username or email already registered'}), 409
    
@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    if not users:
        return jsonify({'Error': 'No user available'}), 404
    return jsonify([user.to_dict() for user in users]), 200

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'Error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'Error': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

order_bp = Blueprint('orders', __name__)

@order_bp.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    if not orders:
        return jsonify({'Error': 'No orders found'}), 404
    return jsonify([order.to_dict() for order in orders]), 200

@order_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if order is None:
        return jsonify({'Error': 'Order not found'}), 404
    return jsonify(order.to_dict()), 200

@order_bp.route('/orders/add', methods=['POST'])
def add_order():
    data = request.get_json()

    if not data.get('user_id') or not data.get('total_price'):
        return jsonify({'Error': 'user id and total price are required'}), 400
    order = Order(
        user_id=data.get('user_id'),
        total_price=data.get('total_price')
    )
    try:
        db.session.add(order)
        db.session.commit()
        return jsonify(order.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'Error': 'Data violates database constraints'}), 409

order_item_bp = Blueprint('order_items', __name__)

@order_item_bp.route('/order_items/add', methods=['POST'])
def add_order_item():
    data = request.get_json()

    if not data.get('order_id') or not data.get('product_id'):
        return jsonify({'Error': 'order id and product id are required'}), 400
    # order_item = order_items(
    #     order_id=data.get('order_id'),
    #     product_id=data.get('product_id')
    # )
    # try:
    #     db.session.add(order_item)
    #     db.session.commit()
    #     return jsonify(order_item.to_dict()), 201
    # except IntegrityError:
    #     db.session.rollback()
    #     return jsonify({'Error': 'Data violates database constraints'}), 409
    try:
        stmt = order_items.insert().values(
            order_id=data.get('order_id'),
            product_id=data.get('product_id')
        )
        db.session.execute(stmt)
        db.session.commit()
        return jsonify({'order_id': data['order_id'], 'product_id': data['product_id']}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'Error': 'Data violates database constraints'}), 409

@order_item_bp.route('/order_items', methods=['GET'])
def get_order_items():
    # order_items = OrderItem.query.all()
    # if not order_items:
    #     return jsonify({'Error': 'No order items found'}), 404
    # return jsonify([oi.to_dict() for oi in order_items]), 200

    result = db.session.execute(order_items.select()).fetchall()
    if not result:
        return jsonify({'Error': 'No order items found'}), 404
    return jsonify([{'order_id': row.order_id, 'product_id': row.product_id} for row in result]), 200

category_bp = Blueprint('categories', __name__)

@category_bp.route('/category/add', methods=['POST'])
def add_category():
    data = request.get_json()

    if not data.get('name'):
        return jsonify({'Error': 'name are required'}), 400
    category = Category(
        name=data.get('name'),
        description=data.get('description'),
    )
    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'Error': 'Data violates database constraints'}), 409

@category_bp.route('/category', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    if not categories:
        return jsonify({'Error': 'No categories found'}), 404
    return jsonify([category.to_dict() for category in categories]), 200

@category_bp.route('/category/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'Error': 'Category not found'}), 404
    return jsonify(category.to_dict()), 200

@category_bp.route('/category/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'Error': 'Category not found'}), 404
    db.session.delete(category)
    db.session.commit()
    return jsonify({'Message': 'Category deleted successfully'}), 200