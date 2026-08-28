from locust import HttpUser, task, between
import random

PRODUCT_IDS = list(range(1, 7))
USER_IDS = list(range(1, 6))

class ShoppingUserJourney(HttpUser):
    wait_time = between(1, 3)

    @task
    def shopping_journey(self):
        self.client.get('/products')

        product_id = random.choice(PRODUCT_IDS)
        self.client.get(f'/products/{product_id}', name='/products/<id>')

        order_resp = self.client.post('/orders', json={
            'user_id': random.choice(USER_IDS),
            'total_price': 100000,
            'product_ids': [product_id]
        })

        if order_resp.status_code == 201:
            order_id = order_resp.json().get('id')
            if order_id:
                self.client.get(f'/orders/{order_id}', name='/orders/<id>')
