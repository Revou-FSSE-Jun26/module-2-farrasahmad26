def validate_order_data(data, require_all=True):
    user_id = data.get('user_id')
    status = data.get('status')
    items = data.get('items')
    valid_status = ['pending', 'completed', 'cancelled']

    if require_all and user_id is None:
        return 'user_id is required', 400
    if user_id is not None:
        if not isinstance(user_id, int) or isinstance(user_id, bool):
            return 'user_id must be a number', 400
        if user_id < 1:
            return 'user_id must be 1 or greater', 422
    
    if status is not None:
        if not isinstance(status, str):
            return 'status must be a string', 400
        if status not in valid_status:
            return 'status input invalid', 400
    
    if require_all and items is None:
        return 'items is required', 400
    if items is not None:
        if not isinstance(items, list) or len(items) == 0:
            return 'items must be a non-empty list', 400
        for item in items:
            if not isinstance(item, dict):
                return 'each item must be an object', 400
            if 'product_id' not in item:
                return 'each item must have product_id', 400
            if not isinstance(item['product_id'], int) or isinstance(item['product_id'], bool):
                return 'product_id must be an integer', 400
            if 'quantity' not in item:
                return 'each item must have quantity', 400
            if not isinstance(item['quantity'], int) or isinstance(item['quantity'], bool):
                return 'quantity must be an integer', 400
            if item['quantity'] < 1:
                return 'quantity must be 1 or greater', 422
    
    return None, None