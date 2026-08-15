# RevoShop

A REST API backend for an e-commerce platform built with Flask and PostgreSQL. RevoShop manages products, categories, users, and orders.

## Database Overview

RevoShop uses a PostgreSQL database (`revoshop_db`) with the following tables:

| Table | Description |
|-------|-------------|
| `users` | Registered users with username, email, password hash, role, and active status |
| `categories` | Product categories |
| `products` | Products with name, description, price, stock quantity, and category reference |
| `orders` | Customer orders with total price, status (pending/processing/delivering), and user reference |
| `order_items` | Association table linking orders to products (many-to-many relationship) |

## ERD (Entity Relationship Diagram)

![ERD Diagram](screenshot%20diagram%20sql.png)

## Repository Structure

```
.
├── app.py                 # Flask application entry point and configuration
├── extensions.py          # SQLAlchemy database instance
├── models.py              # Database models (User, Product, Order, Category, order_items)
├── routes.py              # API route handlers (Blueprints)
├── requirements.txt       # Python dependencies
├── queries.sql            # SQL queries for table creation and seed data
├── schema.sql             # PostgreSQL schema dump
├── seed.sql               # PostgreSQL data dump
├── migrations/            # Alembic database migrations
│   └── versions/          # Migration version files
└── .gitignore
```

## Setup / Installation

### Prerequisites

- Python 3.x
- PostgreSQL

### Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd module-2-farrasahmad26
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create the PostgreSQL database:
   ```sql
   CREATE DATABASE revoshop_db;
   ```

5. Set up the schema and seed data using the SQL files:
   ```bash
   psql -U postgres -d revoshop_db -f schema.sql
   psql -U postgres -d revoshop_db -f seed.sql
   ```

   Or run the migrations:
   ```bash
   flask db upgrade
   ```

6. Run the application:
   ```bash
   flask run
   ```

   The server will start at `http://localhost:5000`.

## API Endpoints

Postman documentation URL:
```
https://documenter.getpostman.com/view/57322437/2sBYApzD2K
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | Get all products |
| GET | `/products/<id>` | Get a product by ID |
| POST | `/products` | Create a new product |
| DELETE | `/products/<id>` | Delete a product |
| GET | `/users` | Get all users |
| GET | `/users/<id>` | Get a user by ID |
| POST | `/users/register` | Register a new user |
| DELETE | `/users/<id>` | Delete a user |
| GET | `/orders` | Get all orders |
| GET | `/orders/<id>` | Get an order by ID |
| POST | `/orders/add` | Create a new order |
| GET | `/order_items` | Get all order items |
| POST | `/order_items/add` | Add a product to an order |
| GET | `/category` | Get all categories |
| GET | `/category/<id>` | Get a category by ID |
| POST | `/category/add` | Create a new category |
| DELETE | `/category/<id>` | Delete a category |
