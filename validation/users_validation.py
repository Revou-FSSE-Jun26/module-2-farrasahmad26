import re

def validate_user_data(data, require_all=True):
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    valid_roles = ['user', 'admin']

    if require_all and username is None:
        return 'username is required', 400
    if username is not None:
        if not isinstance(username, str):
            return 'username must be a string', 400
        if not username.strip():
            return 'username cannot be empty', 400
        if len(username.strip()) > 50:
            return 'username cannot exceed 50 characters', 422
    
    if require_all and email is None:
        return 'email is required', 400
    if email is not None:
        if not isinstance(email, str):
            return 'email must be a string', 400
        if not email.strip():
            return 'email cannot be empty', 400
        if len(email.strip()) > 255:
            return 'email cannot exceed 255 characters', 422
        if not re.match(email_regex, email):
            return 'invalid email format', 400
    
    if require_all and password is None:
        return 'password is required', 400
    if password is not None:
        if not isinstance(password, str):
            return 'password must be a string', 400
        if not password.strip():
            return 'password cannot be empty', 400
        if len(password.strip()) < 8:
            return 'password characters must be 8 or more', 422

    if role is not None:
        if not isinstance(role, str):
            return 'role must be a string', 400
        if role not in valid_roles:
            return 'role must be either user or admin', 400

    return None, None