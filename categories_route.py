from flask import jsonify, request, Blueprint
from extensions import db
from models import Category
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from categories_validation import validate_category_data

category_bp = Blueprint('categories', __name__)

@category_bp.route('/', methods=['GET'])
def get_categories():
    categories = Category.query.filter_by(deleted_at=None).all()
    if not categories:
        return jsonify({'error': 'No available categories'}), 404
    return jsonify([category.to_dict() for category in categories]), 200

@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'error': f'Category {category_id} not found'}), 404
    return jsonify(category.to_dict()), 200

@category_bp.route('/', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    error, code = validate_category_data(data, require_all=True)
    if error:
        return jsonify({'error': error}), code
    category = Category(
        name=data.get('name').strip(),
        description=data.get('description')
    )
    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Data violates database constraints'}), 409
    
@category_bp.route('/<int:category_id>', methods=['PUT'])
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
    if data.get('description') is not None:
        category.description=data['description']

    try:
        db.session.commit()
        return jsonify(category.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'detail': str(e)}), 500
    
@category_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'error': f'Category {category_id} not found'}), 404
    category.deleted_at=datetime.now()
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'}), 200

@category_bp.route('/restore/<int:category_id>', methods=['PUT'])
def restore_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'error': f'Category {category_id} not found'}), 404
    if category.deleted_at is None:
        return jsonify({'error': 'Category is not deleted'}), 400
    category.deleted_at=None
    db.session.commit()
    return jsonify({'message': 'Category restored successfully'}), 200