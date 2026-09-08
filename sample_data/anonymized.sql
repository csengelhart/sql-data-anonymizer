/* Sample MySQL database used to test SQL data anonymization. */
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
  FOREIGN KEY (customer_id) REFERENCES customers (
    customer_id
  )
);

CREATE TABLE shipping (
  shipping_id INT PRIMARY KEY,
  customer_id INT,
  recipient_name VARCHAR(100),
  shipping_address VARCHAR(200),
  contact_phone VARCHAR(30),
  delivery_instructions VARCHAR(200),
  FOREIGN KEY (customer_id) REFERENCES customers (
    customer_id
  )
);

INSERT INTO customers (
  customer_id,
  full_name,
  address,
  email,
  phone,
  account_status
)
VALUES
  (
    101,
    'Daniel Christensen',
    '9748 Grace Glen Apt. 464, Figueroaview, NV 41373',
    'daniel.christensen@example.com',
    '964-555-7372',
    'ACTIVE'
  ),
  (
    102,
    'Rebecca Orr',
    '28266 James Wells, Diazburgh, ND 55416',
    'rebecca.orr@example.com',
    '(678) 555-8707',
    'ACTIVE'
  ),
  (
    103,
    'Nathan Brown',
    '442 David Land, Dickersonberg, AS 46526',
    'nathan.brown@example.com',
    NULL,
    'INACTIVE'
  );

INSERT INTO orders (
  order_id,
  customer_id,
  customer_name,
  contact_email,
  order_total,
  order_date
)
VALUES
  (
    5001,
    101,
    'Daniel Christensen',
    'daniel.christensen@example.com',
    149.99,
    '2026-08-15'
  ),
  (5002, 102, 'Rebecca Orr', 'rebecca.orr@example.com', 87.50, '2026-08-16'),
  (
    5003,
    101,
    'Daniel Christensen',
    'daniel.christensen@example.com',
    42.75,
    '2026-08-17'
  );

INSERT INTO shipping
VALUES
  (
    9001,
    101,
    'Daniel Christensen',
    '9748 Grace Glen Apt. 464, Figueroaview, NV 41373',
    '964-555-7372',
    'Leave package at the front desk'
  ),
  (
    9002,
    102,
    'Rebecca Orr',
    '28266 James Wells, Diazburgh, ND 55416',
    '(678) 555-8707',
    'Signature required'
  ),
  (9003, 103, 'Nathan Brown', '442 David Land, Dickersonberg, AS 46526', NULL, NULL);
