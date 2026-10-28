import re

VALID_STATUS = ['pending', 'completed', 'cancelled']
VALID_SHIPPING = ['regular', 'fast', 'cargo']
VALID_PAYMENT = ['card', 'gopay', 'qris']

# Optional checkout fields stored on the order, with their max length (matches the model).
CHECKOUT_FIELD_LIMITS = {
    'first_name': 100,
    'last_name': 100,
    'phone': 20,
    'company': 150,
    'address': 255,
    'apartment': 255,
    'city': 100,
    'province': 100,
    'postal_code': 10,
    'country': 100,
    'shipping_method': 20,
    'payment_method': 20,
    'note': 500,
}
CHECKOUT_FIELDS = list(CHECKOUT_FIELD_LIMITS)

PHONE_RE = re.compile(r'^(\+62|62|0)8\d{7,11}$')
POSTAL_RE = re.compile(r'^\d{5}$')


def validate_checkout_fields(data):
    for field, limit in CHECKOUT_FIELD_LIMITS.items():
        value = data.get(field)
        if value is None:
            continue
        if not isinstance(value, str):
            return f'{field} must be a string', 400
        if len(value.strip()) > limit:
            return f'{field} cannot exceed {limit} characters', 422

    shipping = data.get('shipping_method')
    if shipping is not None and shipping not in VALID_SHIPPING:
        return 'shipping_method must be one of: ' + ', '.join(VALID_SHIPPING), 400
    payment = data.get('payment_method')
    if payment is not None and payment not in VALID_PAYMENT:
        return 'payment_method must be one of: ' + ', '.join(VALID_PAYMENT), 400

    phone = data.get('phone')
    if phone and not PHONE_RE.match(re.sub(r'[\s-]', '', phone)):
        return 'phone must be a valid Indonesian mobile number', 422
    postal = data.get('postal_code')
    if postal and not POSTAL_RE.match(postal.strip()):
        return 'postal_code must be 5 digits', 422
    return None, None


def validate_order_data(data, require_all=True):
    status = data.get('status')
    items = data.get('items')

    if status is not None:
        if not isinstance(status, str):
            return 'status must be a string', 400
        if status not in VALID_STATUS:
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

    return validate_checkout_fields(data)
