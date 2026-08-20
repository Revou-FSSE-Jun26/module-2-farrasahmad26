def validate_category_data(data, require_all=True):
    name = data.get('name')
    
    if require_all and name is None:
        return 'name is required', 400
    if name is not None:
        if not isinstance(name, str):
            return 'name must be a string', 400
        if not name.strip():
            return 'name cannot be empty', 400
        if len(name.strip()) > 100:
            return 'name cannot exceed 100 characters', 422
    
    return None, None