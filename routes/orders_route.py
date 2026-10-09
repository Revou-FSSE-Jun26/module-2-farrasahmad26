from flask import jsonify, request, Blueprint
from configuration.extensions import db
from model.models import User, Order, Product
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
    
    products = Product.query.filter(Product.id.in_(data['product_ids'])).all()
    if len(products) != len(data['product_ids']):
        return jsonify({'error': 'One or more product id(s) not found'}), 404
    
    order = Order(
        user_id=data.get('user_id'),
        total_price=data.get('total_price'),
        status=data.get('status')
    )
    order.products = products

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