from flask import Flask
from flask_cors import CORS
from configuration.extensions import db
from routes.categories_route import category_bp
from routes.orders_route import order_bp
from routes.products_route import product_bp
from routes.users_route import user_bp
from routes.auth_route import auth_bp
from flask_migrate import Migrate
import os
from datetime import timedelta
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

load_dotenv()

def get_cors_origins():
    # Comma-separated list, e.g. "http://localhost:3000,https://revocoffee.vercel.app".
    # Trailing slashes are stripped because the browser's Origin header never has one.
    raw = os.getenv('CORS_ORIGINS', 'http://localhost:3000')
    return [origin.strip().rstrip('/') for origin in raw.split(',') if origin.strip()]

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": get_cors_origins()}})

    # Default is 15 minutes, which logs shoppers out mid-session.
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    if test_config:
        app.config.update(test_config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    db.init_app(app)
    Migrate(app, db)
    jwt = JWTManager(app)

    # Tokens live for a day, so re-check the user on every request: a deactivated user,
    # or one whose role changed since login, gets 401 and must log in again.
    @jwt.token_in_blocklist_loader
    def token_is_stale(jwt_header, jwt_payload):
        from model.models import User
        user = db.session.get(User, int(jwt_payload['sub']))
        return user is None or not user.can_login or user.role != jwt_payload.get('role')
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