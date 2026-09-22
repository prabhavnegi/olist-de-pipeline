CREATE SCHEMA IF NOT EXISTS mart;

CREATE TABLE mart.dim_customers (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR UNIQUE NOT NULL,
    customer_unique_id VARCHAR,
    customer_zip_code_prefix VARCHAR,
    customer_city VARCHAR,
    customer_state VARCHAR
);

CREATE TABLE mart.dim_products (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR UNIQUE NOT NULL,
    product_category_name VARCHAR,
    product_category_name_english VARCHAR,
    product_weight_g FLOAT,
    product_length_cm FLOAT,
    product_height_cm FLOAT,
    product_width_cm FLOAT,
    product_photos_qty INT
);

CREATE TABLE mart.dim_sellers (
    seller_key SERIAL PRIMARY KEY,
    seller_id VARCHAR UNIQUE NOT NULL,
    seller_zip_code_prefix VARCHAR,
    seller_city VARCHAR,
    seller_state VARCHAR
);

CREATE TABLE mart.dim_dates (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    quarter INT,
    year INT,
    month INT,
    day INT,
    day_of_week INT,
    day_name VARCHAR,
    is_weekend BOOLEAN
);

CREATE TABLE mart.fact_orders (
    order_key SERIAL PRIMARY KEY,
    order_id VARCHAR NOT NULL,
    order_item_id INT,
    customer_key INT REFERENCES mart.dim_customers(customer_key),
    seller_key INT REFERENCES mart.dim_sellers(seller_key),
    product_key INT REFERENCES mart.dim_products(product_key),
    purchase_date_key INT REFERENCES mart.dim_dates(date_key),
    delivered_customer_date_key INT REFERENCES mart.dim_dates(date_key),
    estimated_delivery_date_key INT REFERENCES mart.dim_dates(date_key),
    order_status VARCHAR,
    price NUMERIC,
    freight_value NUMERIC,
    payment_value NUMERIC,
    payment_type VARCHAR,
    payment_installments INT,
    review_score INT
);
