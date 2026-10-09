from flask import jsonify, request, Blueprint
from configuration.extensions import db
from model.models import User
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from validation.users_validation import validate_user_data
from flask_jwt_extended import jwt_required
from validation.validate import owner_required, admin_required

user_bp = Blueprint('users', __name__)

@user_bp.route('', methods=['GET'])
# @jwt_required()
# @admin_required
def get_users():
    users = User.query.filter_by(deleted_at=None).all()
    if not users:
        return jsonify({'error': 'No available user'}), 404
    return jsonify([user.to_dict() for user in users]), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
# @jwt_required()
# @admin_required
# @owner_required
def get_user(user_id):
    user = User.query.filter_by(id=user_id, deleted_at=None).first()
    if user is None:
        return jsonify({'error': f'User {user_id} not found'}), 404
    return jsonify(user.to_dict()), 200

@user_bp.route('', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    error, code = validate_user_data(data, require_all=True)
    if error:
        return jsonify({'error': error}), code
    
    is_user = User.query.filter_by(email=data['email']).first()
    if is_user and is_user.deleted_at:
        # restore yang mana??
        try:
            is_user.deleted_at=None
            db.session.commit()
            return jsonify({'message': 'User restored successfully'}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Failed to restore user'}), 409
    
    is_username = User.query.filter_by(username=data['username']).first()
    if is_username:
        return jsonify({'error': 'Email or username already exists'}), 409

    user = User(
        username=data.get('username').strip(),
        email=data.get('email').strip(),
        role=data.get('role', 'user')
    )

    user.hashing_password(data['password'])

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Something went wrong'}), 409

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.filter_by(id=user_id, deleted_at=None).first()
    if user is None:
        return jsonify({'error': f'User {user_id} not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    error, code = validate_user_data(data, require_all=False)
    if error:
        return jsonify({'error': error}), code
    
    if data.get('username') is not None:
        user.username=data['username'].strip()
    if data.get('email') is not None:
        user.email=data['email'].strip()
    if data.get('is_active') is not None:
        if not isinstance(data['is_active'], bool):
            return jsonify({'error': 'is_active must be a boolean'}), 400
        user.is_active=data['is_active']
    if data.get('password') is not None:
        user.hashing_password(data['password'])
    if data.get('role') is not None:
        user.role=data['role']
    
    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'username or email already registered'}), 409

@user_bp.route('/<int:user_id>', methods=['DELETE'])
# @jwt_required()
# @admin_required
# @owner_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id, deleted_at=None).first()
    if user is None:
        return jsonify({'error': f'User {user_id} not found'}), 404
    user.deleted_at=datetime.now()
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

@user_bp.route('/restore/<int:user_id>', methods=['PUT'])
def restore_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': f'User {user_id} not found'}), 404
    if user.deleted_at is None:
        return jsonify({'error': 'User is not deleted'}), 400
    user.deleted_at=None
    db.session.commit()
    return jsonify({'message': 'User restored successfully'}), 200