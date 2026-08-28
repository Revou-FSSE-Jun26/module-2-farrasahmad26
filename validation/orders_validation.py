def validate_order_data(data, require_all=True):
    user_id = data.get('user_id')
    total_price = data.get('total_price')
    status = data.get('status')
    product_ids = data.get('product_ids')
    valid_status = ['pending', 'completed', 'cancelled']

    if require_all and user_id is None:
        return 'user_id is required', 400
    if user_id is not None:
        if not isinstance(user_id, int) or isinstance(user_id, bool):
            return 'user id must be a number', 400
        if user_id < 1:
            return 'user id must be 1 or greater', 422
    
    if require_all and total_price is None:
        return 'total price is required', 400
    if total_price is not None:
        if not isinstance(total_price, (int, float)) or isinstance(total_price, bool):
            return 'total price must be a number', 400
        if total_price < 0:
            return 'total price must be 0 or greater', 422
    
    if status is not None:
        if not isinstance(status, str):
            return 'status must be a string', 400
        if status not in valid_status:
            return 'status input invalid', 400
    
    if require_all and product_ids is None:
        return 'product id(s) is required', 400
    if product_ids is not None:
        if not isinstance(product_ids, list):
            return 'product id(s) must be a list', 400
        if len(product_ids) == 0:
            return 'product id(s) cannot be empty', 400
        for id in product_ids:
            if not isinstance(id, int) or isinstance(id, bool):
                return 'each product id(s) must be an integer', 400
    
    return None, None