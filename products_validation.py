def validate_product_data(data, require_all=True):
    name = data.get('name')
    price = data.get('price')
    category_id = data.get('category_id')
    stock = data.get('stock_quantity')

    if require_all and name is None:
        return 'name is required', 400
    if name is not None:
        if not isinstance(name, str):
            return 'name must be a string', 400
        if not name.strip():
            return 'name cannot be empty', 400
        if len(name.strip()) > 255:
            return 'name cannot exceed 255 characters', 422
    
    if require_all and price is None:
        return 'price is required', 400
    if price is not None:
        if not isinstance(price, (int,float)) or isinstance(price, bool):
            return 'price must be a number', 400
        if price < 0:
            return 'price must be 0 or greater', 422
    
    if require_all and category_id is None:
        return 'category_id is required', 400
    if category_id is not None:
        if not isinstance(category_id, int) or isinstance(category_id, bool):
            return 'category_id must be an integer', 400
        if not category_id:
            return 'category_id cannot be empty', 400
        if category_id < 0:
            return 'category_id must be 0 or greater', 422
    
    if require_all and stock is None:
        return 'stock quantity is required', 400
    if stock is not None:
        if not isinstance(stock, int) or isinstance(stock, bool):
            return 'stock must be an integer', 400
        if stock < 0:
            return 'stock must be 0 or greater', 422
    
    return None, None