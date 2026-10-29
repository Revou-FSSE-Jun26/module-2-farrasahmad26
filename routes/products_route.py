import re
from flask import jsonify, request, Blueprint
from configuration.extensions import db
from model.models import Product
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from validation.products_validation import validate_product_data
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt
from validation.validate import admin_required

product_bp = Blueprint('products', __name__)

def slugify(text):
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:90] or 'product'
    # A purely numeric slug would be captured by the <int:product_id> route.
    return f'product-{slug}' if slug.isdigit() else slug

def unique_slug(text):
    base = slugify(text)
    slug, n = base, 2
    while Product.query.filter_by(slug=slug).first():
        slug, n = f'{base}-{n}', n + 1
    return slug

@product_bp.route('', methods=['GET'])
def get_products():
    # Public list = active products only. Admins can pass ?include_inactive=true
    # to also get soft-deleted products (dashboard), so they can be reactivated.
    if request.args.get('include_inactive', '').lower() == 'true':
        verify_jwt_in_request()
        if get_jwt().get('role') != 'admin':
            return jsonify({'error': 'Only admin can list inactive products'}), 403
        query = Product.query
    else:
        query = Product.query.filter_by(deleted_at=None)
    category_id = request.args.get('category_id', type=int)
    if category_id is not None:
        query = query.filter_by(category_id=category_id)
    products = query.order_by(Product.id).all()
    if not products:
        return jsonify({'error': 'No available product'}), 404
    return jsonify([product.to_dict() for product in products]), 200

@product_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    error, code = validate_product_data(data, require_all=True)
    if error:
        return jsonify({'error': error}), code
    # Use the client-provided slug if it's a non-empty string, otherwise derive it from the name.
    raw_slug = data.get('slug')
    slug_source = raw_slug if isinstance(raw_slug, str) and raw_slug.strip() else data['name']
    product = Product(
        name=data.get('name').strip(),
        slug=unique_slug(slug_source),
        category_id=data.get('category_id'),
        description=data.get('description'),
        price=data.get('price'),
        stock_quantity=data.get('stock_quantity'),
        image=data.get('image')
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
    # Admins editing a deactivated product need to load it too.
    if request.args.get('include_inactive', '').lower() == 'true':
        verify_jwt_in_request()
        if get_jwt().get('role') != 'admin':
            return jsonify({'error': 'Only admin can view inactive products'}), 403
        if product is None:
            return jsonify({'error': f'Product {product_id} not found'}), 404
        return jsonify(product.to_dict()), 200
    if product is None or product.deleted_at is not None:
        return jsonify({'error': f'Product {product_id} not found'}), 404
    return jsonify(product.to_dict()), 200

@product_bp.route('/<string:slug>', methods=['GET'])
def get_product_by_slug(slug):
    product = Product.query.filter_by(slug=slug, deleted_at=None).first()
    if product is None:
        return jsonify({'error': f'Product {slug} not found'}), 404
    return jsonify(product.to_dict()), 200

@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
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
    # An empty string clears description / image.
    if data.get('description') is not None:
        product.description=data['description'].strip() or None
    if data.get('image') is not None:
        product.image=data['image'].strip() or None

    try:
        db.session.commit()
        return jsonify(product.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'detail': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'error': f'Product {product_id} not found'}), 404
    
    active_orders = [
        oi for oi in product.order_items
        if oi.order is not None and oi.order.deleted_at is None
    ]
    if active_orders:
        return jsonify({'error': 'Product cannot be deleted because it is still used in one or more orders'}), 409
    product.deleted_at=datetime.now()
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200

@product_bp.route('/restore/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def restore_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'error': f'Product {product_id} not found'}), 404
    if product.deleted_at is None:
        return jsonify({'error': 'Product is not deleted'}), 400
    product.deleted_at=None
    db.session.commit()
    return jsonify({'message': 'Product restored successfully', 'product': product.to_dict()}), 200