from flask import jsonify, request, Blueprint
from extensions import db
from models import Product
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from products_validation import validate_product_data

product_bp = Blueprint('products', __name__)

@product_bp.route('/', methods=['GET'])
def get_products():
    products = Product.query.filter_by(deleted_at=None).all()
    if not products:
        return jsonify({'error': 'No available product'}), 404
    return jsonify([product.to_dict() for product in products]), 200

@product_bp.route('/', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    error, code = validate_product_data(data, require_all=True)
    if error:
        return jsonify({'error': error}), code
    product = Product(
        name=data.get('name').strip(),
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
        return jsonify({'error': 'Data violates database constraints'}), 409

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'error': f'Product {product_id} not found'}), 404
    return jsonify(product.to_dict()), 200

@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'error': f'Product {product_id} not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    error, code = validate_product_data(data, require_all=False)
    if error:
        return jsonify({'error': error}), code
    
    if data.get('name') is not None:
        product.name=data['name'].strip()
    if data.get('price') is not None:
        product.price=data['price']
    if data.get('category_id') is not None:
        product.category_id=data['category_id']
    if data.get('stock_quantity') is not None:
        product.stock_quantity=data['stock_quantity']
    if data.get('description') is not None:
        product.description=data['description']

    try:
        db.session.commit()
        return jsonify(product.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'detail': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'error': f'Product {product_id} not found'}), 404
    product.deleted_at=datetime.now()
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200

@product_bp.route('/restore/<int:product_id>', methods=['PUT'])
def restore_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'error': f'Product {product_id} not found'}), 404
    if product.deleted_at is None:
        return jsonify({'error': 'Product is not deleted'}), 400
    product.deleted_at=None
    db.session.commit()
    return jsonify({'message': 'Product restored successfully'}), 200