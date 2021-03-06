import cx_Oracle
import datetime
import names
import random
import string
import lorem
import uuid
import hashlib
from random_word import RandomWords

con = cx_Oracle.connect('system/Djdf1605@localhost/orcle')

def main():
    test()
    insert_emp(20)
    # insert_client(10000)
    # insert_car(10000)
    # insert_product(10000)
    # insert_deal(10000)
    # insert_order(10000)

def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def insert_emp(count=1):
    cur = con.cursor()
    res = cur.execute('select employee_id from employee').fetchall()
    access = ['ADMIN', 'WORKER', 'READER']
    print(random.choice(access))
    for i in range(count):
        test_psw = hash_password('test')
        f_name, s_name, psw, access_type = names.get_first_name(),\
            names.get_last_name(), test_psw, random.choice(access)
        cur = con.cursor()
        info = cur.var(cx_Oracle.STRING)
        cur.callproc('insert_employee', (f_name, s_name, psw, access_type, info))
        print(info.getvalue().capitalize())

def insert_order(count=1):
    cur = con.cursor()
    res = cur.execute('select car_id from car').fetchall()
    car_ids = [id[0] for id in res]
    res = cur.execute('select employee_id from employee where access_type<>\'READER\'').fetchall()
    emp_ids = [id[0] for id in res]
    for i in range(count):
        price, task, car_id, emp_id = random.randint(500, 10000)/100, \
            lorem.sentence(), random.choice(car_ids), random.choice(emp_ids)
        cur = con.cursor()
        info = cur.var(cx_Oracle.STRING)
        cur.callproc('insert_order', (price, task, car_id, emp_id, info))
        print(info.getvalue().capitalize())
    
def insert_deal(count=1):
    cur = con.cursor()
    res = cur.execute('select product_id from product').fetchall()
    prod_ids = [id[0] for id in res]
    res = cur.execute('select client_id from client').fetchall()
    client_ids = [id[0] for id in res]
    res = cur.execute('select employee_id from employee where access_type<>\'READER\'').fetchall()
    emp_ids = [id[0] for id in res]
    for i in range(count):
        product_id, quantity, client_id, emp_id = random.choice(prod_ids), \
            random.randrange(10), random.choice(client_ids), random.choice(emp_ids)
        cur = con.cursor()
        info = cur.var(cx_Oracle.STRING)
        cur.callproc('insert_deal', (product_id, quantity, client_id, emp_id, info))
        print(info.getvalue().capitalize())

def insert_product(count=1):
    words = []
    r = RandomWords()
    for i in range(count):
        words = lorem.paragraph().split(' ')
        product_name, manufacturer, info, price, quantity = \
            random.choice(words).capitalize().replace('.', '').replace(',', ''),\
            random.choice(words).capitalize().replace('.', '').replace(',', ''), \
            lorem.sentence(), random.randint(500, 50000)/100, random.randrange(100)
        cur = con.cursor()
        info_var = cur.var(cx_Oracle.STRING)
        cur.callproc('insert_product', (product_name, manufacturer, info, price, quantity, info_var))
        print(info_var.getvalue().capitalize())
        
def insert_car(count=1):
    words = []
    r = RandomWords()
    cur = con.cursor()
    res = cur.execute('select client_id from client').fetchall()
    ids = [id[0] for id in res]
    for i in range(count):
        words = lorem.paragraph().split(' ')
        make, model, year, vin, client_id = \
            random.choice(words).capitalize().replace(',', '').replace('.', ''),\
            random.choice(words).capitalize().replace(',', '').replace('.', ''), \
            random.randint(1950, datetime.datetime.now().year), \
            random_vin(), random.choice(ids)
        cur = con.cursor()
        info = cur.var(cx_Oracle.STRING)
        cur.callproc('insert_car', (make, model, year, vin, client_id, info))
        print(info.getvalue().capitalize())

def insert_client(count=1):
    for i in range(count):
        f_name, s_name, birthdate, address, phone = \
            names.get_first_name(), names.get_last_name(), \
            datetime.datetime.strptime(random_date(), '%d-%m-%Y'), \
            random_address(), random_phone()
        cur = con.cursor()
        info = cur.var(cx_Oracle.STRING)
        cur.callproc('insert_client', (f_name, s_name, birthdate, address, phone, info))
        print(info.getvalue().capitalize())

def random_vin():
    vin = ''
    for i in range(4):
        vin += random.choice('0123456789')
    letters = string.ascii_lowercase
    vin += ' '
    vin += ''.join(random.choice(letters).capitalize() for i in range(2))
    vin += '-' + random.choice('0123456789')
    return vin

def random_date():
    start = datetime.datetime.strptime('1/1/1920 1:30 PM', '%m/%d/%Y %I:%M %p')
    end = datetime.datetime.now() - datetime.timedelta(days=18*366)
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return (start + datetime.timedelta(seconds=random_second)).strftime('%d-%m-%Y')

def random_phone(length=12):
    phone= '+'
    for i in range(length):
        phone += random.choice('0123456789')
    return str(phone)

def random_address(range=100):
    return str(names.get_last_name() + ' str. ' + \
           str(random.randrange(range)) + ', ' + str(random.randrange(range)))

def test():
    print('Hello world!')

if __name__ == "__main__":
    main()