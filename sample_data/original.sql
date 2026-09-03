-- Sample MySQL database used to test SQL data anonymization.

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    full_name VARCHAR(100),
    address VARCHAR(200),
    email VARCHAR(100),
    phone VARCHAR(30),
    account_status VARCHAR(20)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    customer_name VARCHAR(100),
    contact_email VARCHAR(100),
    order_total DECIMAL(10, 2),
    order_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE shipping (
    shipping_id INT PRIMARY KEY,
    customer_id INT,
    recipient_name VARCHAR(100),
    shipping_address VARCHAR(200),
    contact_phone VARCHAR(30),
    delivery_instructions VARCHAR(200),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

INSERT INTO customers
    (customer_id, full_name, address, email, phone, account_status)
VALUES
    (
        101,
        'John Smith',
        '123 Main Street, Minneapolis, MN 55401',
        'john.smith@gmail.com',
        '612-555-1234',
        'ACTIVE'
    ),
    (
        102,
        'Jane O''Brien',
        '845 Grand Avenue, St. Paul, MN 55105',
        'jane.obrien@yahoo.com',
        '(651) 555-9876',
        'ACTIVE'
    ),
    (
        103,
        'Carlos Rivera',
        '2900 Lake Street, Minneapolis, MN 55408',
        'carlos.rivera@example.org',
        NULL,
        'INACTIVE'
    );

INSERT INTO orders
    (order_id, customer_id, customer_name, contact_email, order_total, order_date)
VALUES
    (
        5001,
        101,
        'John Smith',
        'john.smith@gmail.com',
        149.99,
        '2026-08-15'
    ),
    (
        5002,
        102,
        'Jane O''Brien',
        'jane.obrien@yahoo.com',
        87.50,
        '2026-08-16'
    ),
    (
        5003,
        101,
        'John Smith',
        'john.smith@gmail.com',
        42.75,
        '2026-08-17'
    );

INSERT INTO shipping
VALUES
    (
        9001,
        101,
        'John Smith',
        '123 Main Street, Minneapolis, MN 55401',
        '612-555-1234',
        'Leave package at the front desk'
    ),
    (
        9002,
        102,
        'Jane O''Brien',
        '845 Grand Avenue, St. Paul, MN 55105',
        '(651) 555-9876',
        'Signature required'
    ),
    (
        9003,
        103,
        'Carlos Rivera',
        '2900 Lake Street, Minneapolis, MN 55408',
        NULL,
        NULL
    );