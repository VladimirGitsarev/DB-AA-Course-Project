-------------------------------------TABLES-------------------------------------
CREATE TABLE client 
(
  client_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
  first_name VARCHAR(100),
  second_name VARCHAR(100),
  birthdate DATE, 
  address VARCHAR(100) NOT NULL, 
  phone VARCHAR(20) NOT NULL
);

CREATE TABLE employee
(
  employee_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
  first_name VARCHAR(100),
  second_name VARCHAR(100),
  password_hash VARCHAR(100),
  access_type VARCHAR(50) CHECK (access_type IN ('ADMIN', 'WORKER', 'READER'))
);

CREATE TABLE car
(
  car_id NUMBER(10) GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
  make VARCHAR(50) NOT NULL, 
  model VARCHAR(100) NOT NULL, 
  year NUMBER(10) NOT NULL, 
  vin VARCHAR(10) NOT NULL, 
  client_id NUMBER NOT NULL,
  FOREIGN KEY (client_id)
          REFERENCES client(client_id)
          ON DELETE CASCADE
);

CREATE TABLE product
(
  product_id NUMBER(10) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  product_name VARCHAR(100) NOT NULL, 
  manufacturer VARCHAR(100) NOT NULL,
  info VARCHAR(100) DEFAULT 'NO EXTRA DATA',
  price NUMBER(10,2) DEFAULT NULL,
  quantity NUMBER(10) NOT NULL
);

CREATE TABLE deal
(
  deal_id NUMBER(10) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  deal_date DATE,
  product_id NUMBER(10),
  quantity NUMBER(10) DEFAULT 1,
  client_id NUMBER(10),
  price NUMBER(10, 2) DEFAULT NULL,
  employee_id NUMBER,
  FOREIGN KEY (client_id)
          REFERENCES client(client_id)
          ON DELETE CASCADE,
  FOREIGN KEY (product_id)
          REFERENCES product(product_id)
          ON DELETE CASCADE,
  FOREIGN KEY (employee_id)
          REFERENCES employee(employee_id)
          ON DELETE CASCADE
);

CREATE TABLE orders
(
  order_id NUMBER(10) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_in DATE NOT NULL,
  order_out DATE DEFAULT NULL,
  status VARCHAR(20) DEFAULT 'IN PROGRESS',
  price NUMBER(10, 2),
  task VARCHAR(100),
  car_id NUMBER(10),
  employee_id NUMBER,
  FOREIGN KEY (car_id)
          REFERENCES car(car_id)
          ON DELETE CASCADE,
  FOREIGN KEY (employee_id)
          REFERENCES employee(employee_id)
          ON DELETE CASCADE
);
-------------------------------------TABLES-------------------------------------



-------------------------------------VIEWS--------------------------------------
CREATE OR REPLACE VIEW clients_name AS
  SELECT first_name, second_name 
  FROM client

CREATE OR REPLACE VIEW deals_details AS
  SELECT deal.deal_id, deal.deal_date, client.client_id, client.first_name, 
         client.second_name, product.product_id, product.product_name, 
         product.manufacturer, product.info, deal.quantity, deal.price
  FROM deal INNER JOIN product ON deal.product_id = product.product_id 
            INNER JOIN client ON deal.client_id = client.client_id
  ORDER BY deal.deal_date DESC

CREATE OR REPLACE VIEW employees_details AS
  SELECT * FROM employee order by second_name, first_name
  
CREATE OR REPLACE VIEW orders_details AS
  SELECT orders.order_id, orders.order_in, orders.order_out, orders.task,
         orders.status, orders.car_id, car.make, car.MODEL, car.vin,
         client.client_id, orders.price, client.first_name, client.second_name 
  FROM orders INNER JOIN car ON car.car_id = orders.car_id
              INNER JOIN client ON car.client_id = client.client_id
  ORDER BY orders.order_in, orders.order_out DESC

CREATE OR REPLACE VIEW cars_details AS
  SELECT car.car_id, car.make, car.model, car.vin, car.year,
         client.client_id, client.first_name, client.second_name
         FROM car INNER JOIN client ON car.client_id = client.client_id
  ORDER BY car.make, car.model

CREATE OR REPLACE VIEW products_details AS
  SELECT * FROM product ORDER BY product_name, manufacturer, price, quantity
-------------------------------------VIEWS--------------------------------------



------------------------------------TRIGGERS------------------------------------
CREATE OR REPLACE TRIGGER deal_trigger
  BEFORE INSERT ON deal
  FOR EACH ROW
  DECLARE 
    price_var NUMBER(10, 2);
  BEGIN
    dbms_output.put_line('NEW DEAL ON PRODUCT' ||' '|| :NEW.product_id || ' - ' || :NEW.quantity || ' PIECES' );
    UPDATE product SET quantity = quantity - :NEW.quantity WHERE product_id = :NEW.product_id;
    SELECT price INTO price_var FROM product WHERE product_id = :NEW.product_id;
    :NEW.price := :NEW.quantity * price_var;
  END;
------------------------------------TRIGGERS------------------------------------



----------------------------------PROC & FUNC-----------------------------------
--Clients Procedures-- 
CREATE OR REPLACE PROCEDURE insert_client(
	   p_first_name IN client.first_name%TYPE,
	   p_second_name IN client.second_name%TYPE,
	   p_birthdate IN client.birthdate%TYPE,
	   p_address IN client.address%TYPE,
     p_phone IN client.phone%TYPE,
     p_info out VARCHAR)
IS
BEGIN
  IF p_birthdate > SYSDATE
  THEN
    dbms_output.put_line('BIRTHDATE CAN NOT BE MORE THAN ACTUAL DATE');
    p_info := 'BIRTHDATE CAN NOT BE MORE THAN ACTUAL DATE';
  elsif p_birthdate > SYSDATE-to_yminterval('18-0')
  THEN
    dbms_output.put_line('CLIENT MUST BE OVER 18');
    p_info := 'CLIENT MUST BE OVER 18';
  ELSE
     INSERT INTO client (first_name, second_name, birthdate, address, phone)
     VALUES (p_first_name, p_second_name, p_birthdate, p_address, p_phone);
     p_info := 'NEW CLIENT ADDED';
     COMMIT;
  END IF;
END;

CREATE OR REPLACE PROCEDURE update_client(
  p_client_id IN client.client_id%TYPE,
  p_first_name IN client.first_name%TYPE,
  p_second_name IN client.second_name%TYPE,
  p_birthdate IN client.birthdate%TYPE,
  p_address IN client.address%TYPE,
  p_phone IN client.phone%TYPE,
  p_info OUT VARCHAR)
IS
BEGIN
  IF p_birthdate > SYSDATE
    THEN
      dbms_output.put_line('BIRTHDATE CAN NOT BE MORE THAN ACTUAL DATE');
      p_info := 'BIRTHDATE CAN NOT BE MORE THAN ACTUAL DATE';
    ELSIF p_birthdate > SYSDATE-to_yminterval('18-0')
    THEN
      dbms_output.put_line('CLIENT MUST BE OVER 18');
      p_info := 'CLIENT MUST BE OVER 18';
    ELSE
     UPDATE client SET first_name = p_first_name, second_name = p_second_name, 
     birthdate = p_birthdate, address = p_address, phone = p_phone 
     WHERE client_id = p_client_id; 
     p_info := 'CLIENT ' || p_client_id || ' UPDATED';
     COMMIT;
  END IF;
END;

CREATE OR REPLACE PROCEDURE delete_client(
    p_client_id IN client.client_id%TYPE,
    p_info OUT VARCHAR
)
IS
BEGIN
  DELETE FROM client WHERE client_id = p_client_id;
  p_info := 'CLIENT ' || p_client_id || ' DELETED';
  COMMIT;
END;

CREATE OR REPLACE PACKAGE search_client AS

    TYPE client_record IS record(
      client_id NUMBER, 
      first_name VARCHAR(100),
      second_name VARCHAR(100),
      birthdate DATE, 
      address VARCHAR(100), 
      phone VARCHAR(20));

    TYPE client_table IS TABLE OF client_record;

    FUNCTION search_client
    (
      p_client_id VARCHAR DEFAULT NULL, 
      p_second_name VARCHAR DEFAULT NULL
    )
        RETURN client_table
        pipelined;
END;

CREATE OR REPLACE PACKAGE BODY search_client AS
    FUNCTION search_client
    (
      p_client_id VARCHAR DEFAULT NULL, 
      p_second_name VARCHAR DEFAULT NULL
    )
        RETURN client_table
        pipelined IS
    BEGIN
      IF p_second_name IS NULL AND p_client_id IS NULL THEN
        FOR curr IN
          (
            SELECT * FROM client ORDER BY second_name, first_name
          ) loop  
          pipe ROW (curr);
          END loop;
      elsif p_client_id IS NULL THEN
         FOR curr IN
          (
            SELECT * FROM client WHERE to_char(client_id) = p_second_name OR
            LOWER(second_name) LIKE '%'||LOWER(p_second_name)||'%'
            OR LOWER(first_name) LIKE '%'||LOWER(p_second_name)||'%'
            ORDER BY second_name, first_name
          ) loop  
          pipe ROW (curr);
          END loop;
      ELSE
        FOR curr IN
          (
            SELECT * FROM client WHERE client_id = p_client_id
            ORDER BY second_name, first_name
          ) loop  
          pipe ROW (curr);
          END loop;
        RETURN;
    END IF;
    END search_client;
END;

--Employees Procedures--
CREATE OR REPLACE PROCEDURE insert_employee(
    p_first_name IN employee.first_name%TYPE, 
    p_second_name IN employee.second_name%TYPE,
    p_password IN employee.password_hash%TYPE,
    p_access IN employee.access_type%TYPE,
    p_info_var out VARCHAR)
IS
BEGIN
   INSERT INTO employee(first_name, second_name, password_hash, access_type)
   VALUES (p_first_name, p_second_name, p_password, p_access);
   p_info_var := 'NEW EMPLOYEE ADDED';
   COMMIT;
END;

CREATE OR REPLACE PROCEDURE delete_employee(
  p_employee_id IN employee.employee_id%TYPE,
  p_info_var out VARCHAR
)
IS
BEGIN
  DELETE FROM employee WHERE employee_id = p_employee_id;
  p_info_var := 'EMPLOYEE '|| p_employee_id ||' DELETE';
  COMMIT;
END;

CREATE OR REPLACE PROCEDURE update_employee(
    p_employee_id IN employee.employee_id%TYPE,
    p_first_name IN employee.first_name%TYPE, 
    p_second_name IN employee.second_name%TYPE,
    p_access IN employee.access_type%TYPE,
    p_info_var out VARCHAR)
IS
BEGIN
   UPDATE employee SET first_name = p_first_name, second_name = p_second_name,
   access_type = p_access
   WHERE employee_id = p_employee_id;
   p_info_var := 'EMPLOYEE '|| p_employee_id || ' UPDATED';
   COMMIT;
END;


--Products Procedures--
CREATE OR REPLACE PROCEDURE insert_product(
    p_product_name IN product.product_name%TYPE, 
    p_manufacturer IN product.manufacturer%TYPE,
    p_info IN product.info%TYPE,
    p_price IN product.price%TYPE,
    p_quantity IN product.quantity%TYPE,
    p_info_var out VARCHAR)
IS
BEGIN
   INSERT INTO product (product_name, manufacturer, info, price, quantity)
   VALUES (p_product_name, p_manufacturer, p_info, p_price, p_quantity);
   p_info_var := 'NEW PRODUCT ADDED';
   COMMIT;
END;

CREATE OR REPLACE PROCEDURE update_product(
    p_product_id IN product.product_id%TYPE,
    p_product_name IN product.product_name%TYPE, 
    p_manufacturer IN product.manufacturer%TYPE,
    p_info IN product.info%TYPE,
    p_price IN product.price%TYPE,
    p_quantity IN product.quantity%TYPE,
    p_info_var out VARCHAR)
IS
BEGIN
   UPDATE product SET product_name = p_product_name, manufacturer = p_manufacturer, 
     info = p_info, price = p_price, quantity = p_quantity 
     WHERE product_id = p_product_id; 
     p_info_var := 'PRODUCT ' || p_product_id || ' UPDATED';
     COMMIT;
END;

CREATE OR REPLACE PROCEDURE delete_product(
    p_product_id IN product.product_id%TYPE,
    p_info OUT VARCHAR
)
IS
BEGIN
  DELETE FROM product WHERE product_id = p_product_id;
  p_info := 'PRODUCT ' || p_product_id || ' DELETED';
  COMMIT;
END;

CREATE OR REPLACE PACKAGE search_product AS

    TYPE product_record IS record(
    product_id NUMBER(10),
    product_name VARCHAR(100), 
    manufacturer VARCHAR(100),
    info VARCHAR(100),
    price NUMBER(10,2),
    quantity NUMBER(10));

    TYPE product_table IS TABLE OF product_record;

    FUNCTION search_product
    (
      p_query VARCHAR DEFAULT NULL 
    )
        RETURN product_table
        pipelined;
END;

CREATE OR REPLACE PACKAGE BODY search_product AS
    FUNCTION search_product
    (
      p_query VARCHAR DEFAULT NULL 
    )
        RETURN product_table
        pipelined IS
    BEGIN
      IF p_query IS NULL THEN
        FOR curr IN
          (
            SELECT * FROM products_details
          ) loop  
          pipe ROW (curr);
          END loop;
      ELSE
        FOR curr IN
          (
            SELECT * FROM products_details WHERE to_char(product_id) = p_query OR
            lower(concat(concat(product_name, ' '), manufacturer))
            LIKE '%'|| lower(p_query) || '%'
            OR lower(info) LIKE '%'|| lower(p_query) || '%'
          ) loop  
          pipe ROW (curr);
          END loop;
        RETURN;
    END IF;
    END search_product;
END;

--Cars Procedures--
CREATE OR REPLACE PROCEDURE insert_car(
    p_make IN car.make%TYPE, 
    p_model IN car.model%TYPE,
    p_year IN car.YEAR%TYPE,
    p_vin IN car.vin%TYPE,
    p_client_id IN car.client_id%TYPE,
    p_info_var out VARCHAR)
IS
BEGIN
  IF p_year > EXTRACT (YEAR FROM SYSDATE)
    THEN
    p_info_var := 'YEAR MUST BE LESS THAN CURRENT YEAR';
  ELSE
   INSERT INTO car (make, model, year, vin, client_id)
   VALUES (p_make, p_model, p_year, p_vin, p_client_id);
   p_info_var := 'NEW CAR ADDED';
   COMMIT;
  END IF;
END;

CREATE OR REPLACE PROCEDURE update_car(
    p_car_id IN car.car_id%TYPE,
    p_make IN car.make%TYPE, 
    p_model IN car.model%TYPE,
    p_year IN car.YEAR%TYPE,
    p_vin IN car.vin%TYPE,
    p_info_var out VARCHAR)
IS
BEGIN
  IF p_year > EXTRACT (YEAR FROM SYSDATE)
    THEN      
    p_info_var := 'YEAR MUST BE LESS THAN CURRENT YEAR';
  ELSE
   UPDATE car SET make = p_make, MODEL = p_model, 
     YEAR = p_year, vin = p_vin
     WHERE car_id = p_car_id; 
     p_info_var := 'CAR ' || p_car_id || ' UPDATED';
     COMMIT;
  END IF;
END;

CREATE OR REPLACE PROCEDURE delete_car(
    p_car_id IN product.product_id%TYPE,
    p_info OUT VARCHAR
)
IS
BEGIN
  DELETE FROM car WHERE car_id = p_car_id;
  p_info := 'CAR ' || p_car_id || ' DELETED';
  COMMIT;
END;

CREATE OR REPLACE PACKAGE search_car AS

    TYPE car_record IS record(
          
      car_id NUMBER,
      make VARCHAR(50), 
      MODEL VARCHAR(100), 
      vin VARCHAR(10), 
      YEAR NUMBER,
      client_id NUMBER, 
      first_name VARCHAR(100), 
      second_name VARCHAR(100));
      
    TYPE car_table IS TABLE OF car_record;

    FUNCTION search_car
    (
      p_query VARCHAR DEFAULT NULL
    )
        RETURN car_table
        pipelined;
END;

CREATE OR REPLACE PACKAGE BODY search_car AS
    FUNCTION search_car
    (
      p_query VARCHAR DEFAULT NULL
    )
        RETURN car_table
        pipelined IS
    BEGIN
      IF p_query IS NULL THEN
        FOR curr IN
          (
            SELECT * FROM cars_details
          ) loop  
          pipe ROW (curr);
          END loop;
      ELSE
        FOR curr IN
          (
            SELECT * FROM cars_details WHERE to_char(car_id) = p_query OR
            lower(make) LIKE '%'|| lower(p_query) ||'%'
            OR lower(MODEL) LIKE '%'|| lower(p_query) ||'%' OR lower(vin) LIKE '%'|| lower(p_query) ||'%'
            OR lower(concat(concat(first_name, ' '), second_name)) LIKE '%'|| lower(p_query) ||'%'
          ) loop  
          pipe ROW (curr);
          END loop;
        RETURN;
    END IF;
    END search_car;
END;


--Deals Procedures--
CREATE OR REPLACE PROCEDURE insert_deal(
    p_product_id IN deal.product_id%TYPE,
    p_quantity IN deal.quantity%TYPE,
    p_client_id IN deal.client_id%TYPE,
    p_employee_id IN deal.employee_id%TYPE,
    info OUT VARCHAR
    )
IS
  product_number NUMBER(10);
BEGIN
  SELECT quantity INTO product_number FROM product
  WHERE product_id = p_product_id;
  IF product_number < p_quantity
    THEN
    info := 'NOT ENOUGH PRODUCTS: '|| product_number ||' LEFT';
  ELSE
    INSERT INTO deal(deal_date, product_id, quantity, client_id, employee_id)
    VALUES(SYSDATE, p_product_id, p_quantity, p_client_id, p_employee_id);
    info := 'NEW DEAL CREATED';
  END IF;
  COMMIT;
END;

CREATE OR REPLACE PACKAGE search_deal AS

    TYPE deal_record IS record(
                
      deal_id NUMBER, 
      deal_date DATE, 
      client_id NUMBER, 
      first_name VARCHAR(100), 
      second_name VARCHAR(100), 
      product_id NUMBER, 
      product_name VARCHAR(100), 
      manufacturer VARCHAR(100), 
      info VARCHAR(100), 
      quantity NUMBER, 
      price NUMBER(10,2));
      
    TYPE deal_table IS TABLE OF deal_record;

    FUNCTION search_deal
    (
      p_query VARCHAR DEFAULT NULL
    )
        RETURN deal_table
        pipelined;
END;

CREATE OR REPLACE PACKAGE BODY search_deal AS
    FUNCTION search_deal
    (
      p_query VARCHAR DEFAULT NULL
    )
        RETURN deal_table
        pipelined IS
    BEGIN
      IF p_query IS NULL THEN
        FOR curr IN
          (
            SELECT * FROM deals_details
          ) loop  
          pipe ROW (curr);
          END loop;
      ELSE
        FOR curr IN
          (
            SELECT * FROM deals_details WHERE to_char(deal_id) = p_query OR
            lower(concat(concat(first_name, ' '), second_name)) LIKE '%'|| lower(p_query) ||'%'
          ) loop  
          pipe ROW (curr);
          END loop;
        RETURN;
    END IF;
    END search_deal;
END;

--Orders Procedures--
CREATE OR REPLACE PROCEDURE insert_order(
    p_price IN orders.price%TYPE,
    p_task IN orders.task%TYPE,
    p_car_id IN orders.car_id%TYPE,
    p_employee_id IN orders.employee_id%TYPE,
    info OUT VARCHAR
    )
IS
BEGIN
  INSERT INTO orders(order_in, price, task, car_id, employee_id)
  VALUES(SYSDATE, p_price, p_task, p_car_id, p_employee_id);
  info := 'NEW ORDER CREATED';
  COMMIT;
END;

CREATE OR REPLACE PROCEDURE update_order(
    p_order_id IN orders.order_id%TYPE,
    info OUT VARCHAR
    )
IS
BEGIN
  UPDATE orders SET status = 'COMPLETED', order_out = SYSDATE
  WHERE order_id = p_order_id;
  info := 'ORDER '|| p_order_id ||' COMPLETED';
  COMMIT;
END;

CREATE OR REPLACE PACKAGE search_order AS

    TYPE order_record IS record(
      order_id NUMBER, 
      order_in DATE,
      order_out DATE,
      task varchar(100),
      status VARCHAR(50),
      car_id NUMBER, 
      make VARCHAR(50), 
      model VARCHAR(100),
      vin VARCHAR(10),
      client_id NUMBER,
      price NUMBER(10,2),
      first_name VARCHAR(100),
      second_name varchar(100));

    TYPE order_table IS TABLE OF order_record;

    FUNCTION search_order_id
    (
      p_order_id NUMBER DEFAULT NULL
    )
        RETURN order_table
        pipelined;
        
    FUNCTION search_order_name
    (
      p_second_name VARCHAR DEFAULT NULL
    )
        RETURN order_table
        pipelined;
    
    FUNCTION search_order_date
    (
      p_date DATE DEFAULT NULL
    )
        RETURN order_table
        pipelined;
        
    FUNCTION search_order_all
    (
      p_active VARCHAR DEFAULT NULL
    )
        RETURN order_table
        pipelined;
END;

CREATE OR REPLACE PACKAGE BODY search_order AS
    FUNCTION search_order_id
    (
      p_order_id NUMBER DEFAULT NULL
    )
        RETURN order_table
        pipelined IS
    BEGIN
        FOR curr IN
          (
            SELECT * FROM orders_details WHERE order_id = p_order_id
          ) loop  
          pipe ROW (curr);
          END loop;
    END search_order_id;
    
    FUNCTION search_order_name
    (
      p_second_name VARCHAR DEFAULT NULL
    )
        RETURN order_table
        pipelined IS
    BEGIN
     FOR curr IN
          (
            SELECT * FROM orders_details 
            WHERE second_name LIKE '%'||p_second_name||'%'
          ) loop  
          pipe ROW (curr);
          END loop;
    END search_order_name;
    
    FUNCTION search_order_date
    (
      p_date DATE DEFAULT NULL
    )
        RETURN order_table
        pipelined IS
    BEGIN
      FOR curr IN
          (
            SELECT * FROM orders_details 
            WHERE to_char(order_in, 'DD.MM.YYYY') = to_char(p_date, 'DD.MM.YYYY')
            OR to_char(order_out, 'DD.MM.YYYY') = to_char(p_date, 'DD.MM.YYYY')
          ) loop  
          pipe ROW (curr);
          END loop;
    END search_order_date;
    
    FUNCTION search_order_all
    (
      p_active VARCHAR DEFAULT NULL
    )
        RETURN order_table
        pipelined IS
    BEGIN
      IF p_active = 'TRUE' THEN
         FOR curr IN
          (
            SELECT * FROM orders_details 
            WHERE status = 'IN PROGRESS'
          ) loop  
          pipe ROW (curr);
          END loop;
      ELSIF p_active = 'FALSE' THEN
        FOR curr IN
          (
            SELECT * FROM orders_details 
            WHERE status = 'COMPLETED'
          ) loop  
          pipe ROW (curr);
          END loop;
      ELSE
        FOR curr IN
          (
            SELECT * FROM orders_details 
          ) loop  
          pipe ROW (curr);
          END loop;
      END IF;
    END search_order_all;
END;
----------------------------------PROC & FUNC-----------------------------------



-------------------------------------SELECTS------------------------------------
SELECT * FROM TABLE(search_client.search_client());
SELECT * FROM TABLE(search_order.search_order_id(5));
SELECT * FROM TABLE(search_order.search_order_name('avad'));
SELECT * FROM TABLE(search_order.search_order_date('19-05-2020'));
SELECT * FROM TABLE(search_order.search_order_all());
SELECT * FROM TABLE(search_car.search_car());
SELECT * FROM TABLE(search_product.search_product());
SELECT * FROM TABLE(search_deal.search_deal('gavr'))
SELECT * FROM deals_details
SELECT * FROM orders_details
SELECT * FROM cars_details
SELECT * FROM products_details
SELECT * FROM employees_details
SELECT * FROM client
SELECT * FROM car
select * from employee
SELECT * FROM product
SELECT * FROM deal
SELECT * FROM orders
-------------------------------------SELECTS------------------------------------



-------------------------------INSERTION EXAMPLES-------------------------------
INSERT INTO client(first_name, second_name, birthdate, address, phone) 
VALUES('John', 'Doe', '01-01-2000', 'New-York, 93426 street, 1', '+7223534657');

INSERT INTO car(make, model, year, vin, client_id) 
VALUES('Tesla', 'Model S', 2018, 'MYTESLA', 1);

INSERT INTO product(product_name, manufacturer, info, price, quantity) 
VALUES ('Tyre', 'Belshina', 'Bel-203 215/55R16 93H (2015)', 29.99, 100);

INSERT INTO deal(deal_date, product_id, quantity, client_id) 
VALUES (SYSDATE, 1, 1, 1);

INSERT INTO orders(order_in, status, price, task, car_id, employee_id)
values (sysdate)

INSERT INTO employee(first_name, second_name, password_hash, access_type)
VALUES ('Uladzimir', 'Hitsarau', 
'3bf078263e9c75e54a63ab5c8f2e82acb7e9d78157824e914d78c5678404fad1:e6f6a3d282db4a44b9a9b12b3714115d',
'ADMIN');
-------------------------------INSERTION EXAMPLES------------------------------- 



--------------------------------------DROPS-------------------------------------
DROP TABLE CAR;
DROP TABLE EMPLOYEE;
DROP TABLE CLIENT;
DROP TABLE PRODUCT;
DROP TABLE DEAL;
DROP TABLE ORDERS;
--------------------------------------DROPS-------------------------------------