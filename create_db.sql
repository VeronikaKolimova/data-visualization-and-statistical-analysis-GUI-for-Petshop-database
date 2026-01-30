PRAGMA foreign_keys = OFF;


CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    customer_phone TEXT
);

CREATE TABLE goods (
    product_id INTEGER PRIMARY KEY ,
    product_name TEXT,
    decription TEXT,
    unit_of_measure TEXT
);

CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY,
    supplier_name TEXT,
    phone_supplier TEXT
);

CREATE TABLE purchases (
    purchase_id INTEGER PRIMARY KEY,
    purchase_date DATE,
    supplier_id INTEGER,
    product_id INTEGER,
    purchase_qnty INTEGER,
    purchase_price INTEGER,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (product_id) REFERENCES goods(product_id)
);

CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    sale_date DATE,
    customer_id INTEGER,
    product_id INTEGER,
    sale_qnty INTEGER,
    sale_price INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES goods(product_id)
);
