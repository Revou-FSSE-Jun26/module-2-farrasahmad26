from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt

def owner_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):

        current_user_id = get_jwt_identity()
        requested_user_id = kwargs.get('user_id')

        if str(current_user_id) != str(requested_user_id):
            return jsonify({
                'error': 'You are not allowed to access this resource'
            }), 403

        return fn(*args, **kwargs)
    
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()

        role = claims['role']

        if role != 'admin':
            return {
                'success': False,
                'message': 'Only admin can access this routes'
            }, 403
        
        return fn(*args, **kwargs)
    
    return wrapper