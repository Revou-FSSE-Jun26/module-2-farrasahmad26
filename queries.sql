create table users (
id SERIAL primary key,
username varchar(50) not null unique,
email varchar(255) not null unique,
password_hash varchar(255) not null,
is_active boolean not null default true,
created_at timestamp not null default now()
);

create table categories (
id SERIAL primary key,
name varchar(100) not null,
description text,
is_active boolean not null default true,
created_at timestamp not null default now()
);

create table products (
id SERIAL primary key,
name varchar(255) not null,
category_id integer not null,
description text,
price numeric(10,2) not null,
stock_quantity integer not null,
created_at timestamp not null default now(),
constraint fk_product_category foreign key (category_id) references categories(id)
);

create table orders (
id SERIAL primary key,
user_id integer not null,
total_price numeric(10,2) not null check (total_price >= 0),
status varchar(50) not null default 'pending',
ordered_at timestamp not null default now(),
constraint fk_orders_user foreign key (user_id) references users(id)
);

create table order_items (
order_id integer not null,
product_id integer not null,
quantity integer not null default 1 check (quantity > 0),
primary key (order_id, product_id),
constraint fk_oi_order foreign key (order_id) references orders(id) on delete cascade,
constraint fk_oi_product foreign key (product_id) references products(id)
);

insert into users (username, email, password_hash)
values ('Budi', 'budi123@email.com', 'password123'),
('Andi', 'andi123@email.com', 'wordpass123'),
('Dika', 'dika456@email.com', 'rahasi123'),
('Abdul', 'abdul789@email.com', 'apaantuh456'),
('Joko', 'joko666@email.com', 'xixixi555');

insert into categories (name, description)
values ('Arabica', 'Biji kopi 100% Arabica'),
('Robusta', 'Biji kopi 100% Robusta'),
('Blend', 'Biji kopi 50% Arabica 50% Robusta'),
('Liberica', 'Biji kopi 100% Liberica'),
('Excelsa', 'Biji kopi 100% Excelsa');

insert into products (name, category_id, description, price, stock_quantity)
values ('Arabica Sidikalang', 1, 'Flavor Notes: Spices, Cinnamon, Lemon zest. Netto 200 gram', 85000, 50),
('Arabica Mandailing', 1, 'Flavor Notes: Malt, Nutty, Bitter Sweet, Floral. Netto 200 gram', 94000, 50),
('Robusta Lampung', 2, 'Flavor Notes: Dark cocoa, Nutty, Caramelized. Netto 200 gram', 65000, 70),
('Excelsa Muria', 5, 'Flavor Notes: Chocolate, Floral, Brown Sugar. Netto 200 gram', 40000, 20),
('Little Sweet Liberica', 4, 'Flavor Notes: Fruity, Nutty, Sweet, Spicy, Smoky, Little Bit of Mint. Netto 200 gram', 100000, 60),
('Italian Blend', 3, 'Flavor Notes: Brown Sugar, Sweet, Strong, Chocolate. Netto 200 gram', 80000, 90);

insert into orders (user_id, total_price, status)
values (2, 94000, 'pending'),
(1, 85000, 'processing'),
(4, 80000, 'delivering'),
(3, 100000, 'pending');

insert into order_items (order_id, product_id, quantity)
values (1, 2, 1),
(2, 1, 1),
(3, 6, 1),
(4, 5, 1);

select * from orders
where total_price > 90000;

select * from products
where price > 70000
order by price desc
limit 3;