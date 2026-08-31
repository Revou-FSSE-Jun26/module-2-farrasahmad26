from flask import Flask
from configuration.extensions import db
from routes.categories_route import category_bp
from routes.orders_route import order_bp
from routes.products_route import product_bp
from routes.users_route import user_bp
from routes.auth_route import auth_bp
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    db.init_app(app)
    Migrate(app, db)
    jwt = JWTManager(app)
    app.register_blueprint(product_bp, url_prefix='/products')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(category_bp, url_prefix='/categories')

    return app

if __name__ == '__main__':
    app = create_app()
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)