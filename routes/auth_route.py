from flask import Blueprint, request, jsonify
from configuration.extensions import db
from model.models import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400

    is_user = User.query.filter_by(email=email).first()
    if is_user is None or not is_user.check_password(password):
        return jsonify({'success': False, 'message': 'wrong email or password'}), 401
    
    access_token = create_access_token(
        identity=str(is_user.id),
        additional_claims={
            'email': is_user.email,
            'role': is_user.role
        }
    )

    return jsonify({
        'success': True,
        'message' : 'real user',
        'access_token': access_token
    }), 200