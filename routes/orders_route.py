from decimal import Decimal
from flask import jsonify, request, Blueprint
from configuration.extensions import db
from model.models import User, Order, Product, OrderItem
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from validation.orders_validation import validate_order_data, CHECKOUT_FIELDS
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from validation.validate import admin_required

order_bp = Blueprint('orders', __name__)

# Must match SHIPPING_METHODS in the frontend (src/lib/checkout.ts).
FREE_SHIPPING_THRESHOLD = Decimal('50')
SHIPPING_PRICES = {'regular': Decimal('5'), 'fast': Decimal('15'), 'cargo': Decimal('8')}
FREE_OVER_THRESHOLD = {'regular'}


def shipping_cost_for(method, subtotal):
    """Shipping is recalculated here so a client can't send its own price."""
    if method is None:
        return Decimal('0')
    if method in FREE_OVER_THRESHOLD and subtotal >= FREE_SHIPPING_THRESHOLD:
        return Decimal('0')
    return SHIPPING_PRICES[method]


def current_user_id():
    return int(get_jwt_identity())


def is_admin():
    return get_jwt().get('role') == 'admin'


def find_visible_order(order_id):
    """Returns the order if the caller may see it. Other users' orders look like 404
    so their existence isn't leaked."""
    order = Order.query.filter_by(id=order_id, deleted_at=None).first()
    if order is None or (not is_admin() and order.user_id != current_user_id()):
        return None
    return order


@order_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    query = Order.query.filter_by(deleted_at=None)
    # Admins see every order (dashboard); everyone else only their own.
    if not is_admin():
        query = query.filter_by(user_id=current_user_id())
    orders = query.order_by(Order.id.desc()).all()
    if not orders:
        return jsonify({'error': 'No available order'}), 404
    return jsonify([order.to_dict() for order in orders]), 200


@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    order = find_visible_order(order_id)
    if order is None:
        return jsonify({'error': f'Order {order_id} not found'}), 404
    return jsonify(order.to_dict()), 200


@order_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    error, code = validate_order_data(data, require_all=True)
    if error:
        return jsonify({'error': error}), code

    # The buyer is always the logged-in user; any user_id in the body is ignored.
    user = User.query.get(current_user_id())
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    products_ids = [item['product_id'] for item in data['items']]
    products = {
        p.id: p for p in Product.query.filter(Product.id.in_(products_ids), Product.deleted_at.is_(None)).all()
    }
    if len(products) != len(set(products_ids)):
        return jsonify({'error': 'One or more product_id(s) not found'}), 404

    subtotal = Decimal('0')
    order_items_list = []
    for item in data['items']:
        product = products[item['product_id']]
        qty = item['quantity']
        subtotal += product.price * qty
        order_items_list.append(OrderItem(
            product_id=product.id,
            quantity=qty,
            price_at_order=product.price
        ))

    shipping_cost = shipping_cost_for(data.get('shipping_method'), subtotal)

    order = Order(
        user_id=user.id,
        total_price=subtotal + shipping_cost,
        shipping_cost=shipping_cost,
        # New orders always start as pending; clients can't create completed orders.
        status='pending',
        **{field: (data[field].strip() or None) if isinstance(data.get(field), str) else None
            for field in CHECKOUT_FIELDS},
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
@jwt_required()
def update_order(order_id):
    order = find_visible_order(order_id)
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

    status = data.get('status')
    if status is not None:
        # Customers may only cancel their own order; any other status change is admin-only.
        if status != 'cancelled' and not is_admin():
            return jsonify({'error': 'Only admin can change the order status to ' + status}), 403
        order.status = status

    try:
        db.session.commit()
        return jsonify(order.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'detail': str(e)}), 500


@order_bp.route('/<int:order_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_order(order_id):
    order = Order.query.filter_by(id=order_id, deleted_at=None).first()
    if order is None:
        return jsonify({'error': f'Order {order_id} not found'}), 404
    order.deleted_at=datetime.now()
    db.session.commit()
    return jsonify({'message': 'Order deleted successfully'}), 200
