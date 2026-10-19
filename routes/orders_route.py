from flask import jsonify, request, Blueprint
from configuration.extensions import db
from model.models import User, Order, Product, OrderItem
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from validation.orders_validation import validate_order_data
from flask_jwt_extended import jwt_required
from validation.validate import owner_required, admin_required

order_bp = Blueprint('orders', __name__)

@order_bp.route('', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    if not orders:
        return jsonify({'error': 'No available order'}), 404
    return jsonify([order.to_dict() for order in orders]), 200

@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': f'Order {order_id} not found'}), 404
    return jsonify(order.to_dict()), 200

@order_bp.route('', methods=['POST'])
# @jwt_required()
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    error, code = validate_order_data(data, require_all=True)
    if error:
        return jsonify({'error': error}), code
    
    user = User.query.get(data['user_id'])
    if user is None:
        return jsonify({'error': f'User {data["user_id"]} not found'}), 404
    
    products_ids = [item['product_id'] for item in data['items']]
    products = {p.id: p for p in Product.query.filter(Product.id.in_(products_ids)).all()}
    if len(products) != len(set(products_ids)):
        return jsonify({'error': 'One or more product_id(s) not found'}), 404

    total_price = 0
    order_items_list = []
    for item in data['items']:
        product = products[item['product_id']]
        qty = item['quantity']
        total_price += product.price * qty
        order_items_list.append(OrderItem(
            product_id=product.id,
            quantity=qty,
            price_at_order=product.price
        ))
    
    order = Order(
        user_id=data['user_id'],
        total_price=total_price,
        status=data.get('status', 'pending')
    )
    order.order_items = order_items_list

    try:
        db.session.add(order)
        db.session.commit()
        return jsonify(order.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Data violates database constraints'}), 409

@order_bp.route('/<int:order_id>', methods=['PUT'])
# @jwt_required()
# @admin_requried
def update_order(order_id):
    order = Order.query.get(order_id)
    if order is None:
        return jsonify({'error': f'Order {order_id} not found'}), 404
    if order.status in ['completed', 'cancelled']:
        return jsonify({'error': 'Cannot update a completed or cancelled order'}), 400
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    error, code = validate_order_data(data, require_all=False)
    if error:
        return jsonify({'error': error}), code

    if data.get('status') is not None:
        order.status=data['status']

    try:
        db.session.commit()
        return jsonify(order.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'detail': str(e)}), 500

@order_bp.route('/<int:order_id>', methods=['DELETE'])
# @jwt_required()
# @admin_requried
def delete_order(order_id):
    order = Order.query.filter_by(id=order_id, deleted_at=None).first()
    if order is None:
        return jsonify({'error': f'Order {order_id} not found'}), 404
    order.deleted_at=datetime.now()
    db.session.commit()
    return jsonify({'message': 'Order deleted successfully'}), 200