from flask import jsonify, request, Blueprint
from configuration.extensions import db
from model.models import User
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from validation.users_validation import validate_user_data
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt, get_jwt_identity
from validation.validate import admin_required

user_bp = Blueprint('users', __name__)


def include_inactive():
    return request.args.get('include_inactive', '').lower() == 'true'


def is_self(user):
    return str(user.id) == str(get_jwt_identity())


def email_taken(email, exclude_id=None):
    # Case-insensitive, and includes deactivated users: their email stays reserved.
    query = User.query.filter(func.lower(User.email) == email.strip().lower())
    if exclude_id is not None:
        query = query.filter(User.id != exclude_id)
    return query.first() is not None


def username_taken(username, exclude_id=None):
    query = User.query.filter(func.lower(User.username) == username.strip().lower())
    if exclude_id is not None:
        query = query.filter(User.id != exclude_id)
    return query.first() is not None


@user_bp.route('', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    # Admin dashboard; ?include_inactive=true also returns deactivated users.
    query = User.query if include_inactive() else User.query.filter_by(deleted_at=None)
    users = query.order_by(User.id).all()
    if not users:
        return jsonify({'error': 'No available user'}), 404
    return jsonify([user.to_dict() for user in users]), 200


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    query = User.query.filter_by(id=user_id)
    if not include_inactive():
        query = query.filter_by(deleted_at=None)
    user = query.first()
    if user is None:
        return jsonify({'error': f'User {user_id} not found'}), 404
    return jsonify(user.to_dict()), 200


@user_bp.route('', methods=['POST'])
def create_user():
    """Public registration. Only an admin token may create users with a role other than 'user'."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    error, code = validate_user_data(data, require_all=True)
    if error:
        return jsonify({'error': error}), code

    verify_jwt_in_request(optional=True)
    caller_is_admin = (get_jwt() or {}).get('role') == 'admin'
    role = data.get('role', 'user') if caller_is_admin else 'user'

    # Deactivated accounts are NOT silently restored by re-registering: that would let a
    # banned user back in. Their email/username stay taken until an admin restores them.
    if email_taken(data['email']) or username_taken(data['username']):
        return jsonify({'error': 'Email or username already exists'}), 409

    user = User(
        username=data['username'].strip(),
        email=data['email'].strip(),
        role=role,
    )
    user.hashing_password(data['password'])
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email or username already exists'}), 409


@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': f'User {user_id} not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    error, code = validate_user_data(data, require_all=False)
    if error:
        return jsonify({'error': error}), code

    if data.get('role') is not None and data['role'] != user.role and is_self(user):
        return jsonify({'error': 'You cannot change your own role'}), 400
    if data.get('email') is not None and email_taken(data['email'], exclude_id=user.id):
        return jsonify({'error': 'Email already registered'}), 409
    if data.get('username') is not None and username_taken(data['username'], exclude_id=user.id):
        return jsonify({'error': 'Username already registered'}), 409

    if data.get('username') is not None:
        user.username = data['username'].strip()
    if data.get('email') is not None:
        user.email = data['email'].strip()
    if data.get('password') is not None:
        user.hashing_password(data['password'])
    if data.get('role') is not None:
        user.role = data['role']
    # Status is changed only via DELETE (deactivate) / restore, so is_active is ignored here.

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'username or email already registered'}), 409


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id, deleted_at=None).first()
    if user is None:
        return jsonify({'error': f'User {user_id} not found'}), 404
    if is_self(user):
        return jsonify({'error': 'You cannot deactivate your own account'}), 400
    user.deleted_at = datetime.now()
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


@user_bp.route('/restore/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def restore_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': f'User {user_id} not found'}), 404
    if user.deleted_at is None:
        return jsonify({'error': 'User is not deleted'}), 400
    user.deleted_at = None
    db.session.commit()
    return jsonify({'message': 'User restored successfully', 'user': user.to_dict()}), 200
