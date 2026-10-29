from flask import jsonify, request, Blueprint
from configuration.extensions import db
from model.models import Category
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from validation.categories_validation import validate_category_data
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt
from validation.validate import admin_required

category_bp = Blueprint('categories', __name__)


def wants_inactive():
    """?include_inactive=true is admin-only. Returns (flag, error_response)."""
    if request.args.get('include_inactive', '').lower() != 'true':
        return False, None
    verify_jwt_in_request()
    if get_jwt().get('role') != 'admin':
        return True, (jsonify({'error': 'Only admin can view inactive categories'}), 403)
    return True, None


@category_bp.route('', methods=['GET'])
def get_categories():
    # Public list = active categories. Admins can add ?include_inactive=true (dashboard).
    include_inactive, error = wants_inactive()
    if error:
        return error
    query = Category.query if include_inactive else Category.query.filter_by(deleted_at=None)
    categories = query.order_by(Category.id).all()
    if not categories:
        return jsonify({'error': 'No available categories'}), 404
    return jsonify([category.to_dict() for category in categories]), 200


@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    include_inactive, error = wants_inactive()
    if error:
        return error
    category = Category.query.get(category_id)
    if category is None or (category.deleted_at is not None and not include_inactive):
        return jsonify({'error': f'Category {category_id} not found'}), 404
    return jsonify(category.to_dict(include_products=True)), 200


@category_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    error, code = validate_category_data(data, require_all=True)
    if error:
        return jsonify({'error': error}), code
    category = Category(
        name=data.get('name').strip(),
        description=(data.get('description') or '').strip() or None,
        image=(data.get('image') or '').strip() or None
    )
    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Data violates database constraints'}), 409


@category_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'error': f'Category {category_id} not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    error, code = validate_category_data(data, require_all=False)
    if error:
        return jsonify({'error': error}), code

    if data.get('name') is not None:
        category.name=data['name'].strip()
    # Empty strings clear description / image.
    if data.get('description') is not None:
        category.description=data['description'].strip() or None
    if data.get('image') is not None:
        category.image=data['image'].strip() or None

    try:
        db.session.commit()
        return jsonify(category.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'detail': str(e)}), 500


@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(category_id):
    category = Category.query.filter_by(id=category_id, deleted_at=None).first()
    if category is None:
        return jsonify({'error': f'Category {category_id} not found'}), 404
    # Don't leave active products without a visible category in the shop.
    active = category.active_product_count()
    if active:
        return jsonify({
            'error': f'Category cannot be deactivated because it still has {active} active product(s)'
        }), 409
    category.deleted_at=datetime.now()
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'}), 200


@category_bp.route('/restore/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required
def restore_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'error': f'Category {category_id} not found'}), 404
    if category.deleted_at is None:
        return jsonify({'error': 'Category is not deleted'}), 400
    category.deleted_at=None
    db.session.commit()
    return jsonify({'message': 'Category restored successfully', 'category': category.to_dict()}), 200
