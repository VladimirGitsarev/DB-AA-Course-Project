import cx_Oracle
import datetime

con = cx_Oracle.connect('system/Djdf1605@localhost/orcle')

def main():
    print('Hello world!')
    # search_order()
    # update_order()
    # insert_order()
    # insert_deal()
    # delete_car(41)
    # update_car(24)
    # insert_car()
    # delete_product(62)
    # update_product(61)
    # insert_product()
    # delete_client(61)
    # update_client(41)
    search_client(None, None)
    # insert_client()
    # test()

def search_order():
    result_set = []
    param = datetime.datetime.strptime('19-05-2020', '%d-%m-%Y')
    queries = ['SELECT * FROM TABLE(search_order.search_order_id(:param))', \
               'SELECT * FROM TABLE(search_order.search_order_name(:param))',
               'SELECT * FROM TABLE(search_order.search_order_date(:param))']
    cur = con.cursor()
    for q in queries:
        try:
            cur.execute(q, {'param':param})
            res = cur.fetchall()
            for item in res:
                result_set.append(item)
        except:
            pass
    for item in result_set:
        print(item)

def update_order():
    order_id = 2
    cur = con.cursor()
    info = cur.var(cx_Oracle.STRING)
    cur.callproc('update_order', (order_id, info))
    print(info.getvalue().capitalize())

def insert_order():
    price, task, car_id = 20.49, 'Car Wash', 1
    cur = con.cursor()
    info = cur.var(cx_Oracle.STRING)
    cur.callproc('insert_order', (price, task, car_id, info))
    print(info.getvalue().capitalize())

def insert_deal():
    product_id, quantity, client_id = 1, 2, 3
    cur = con.cursor()
    info = cur.var(cx_Oracle.STRING)
    cur.callproc('insert_deal', (product_id, quantity, client_id,))
    print(info.getvalue().capitalize())

def delete_car(product_id):
    cur = con.cursor()
    info = cur.var(cx_Oracle.STRING)
    cur.callproc('delete_car', (product_id, info))
    print(info.getvalue().capitalize())

def update_car(car_id):
    cur = con.cursor()
    info_var = cur.var(cx_Oracle.STRING)
    cur.execute('SELECT * FROM car WHERE car_id = :id', {'id':car_id})
    res = cur.fetchone()
    car_id, make, model, year, vin, client_id = res
    year = 2019
    cur.callproc('update_car', (car_id, make, model, year, vin, info_var))
    print(info_var.getvalue().capitalize())

def insert_car():
    make, model, year, vin, client_id = 'Renualt', 'Clio', 2004, '2904 AT-5', 41
    cur = con.cursor()
    info = cur.var(cx_Oracle.STRING)
    cur.callproc('insert_car', (make, model, year, vin, client_id, info))
    print(info.getvalue().capitalize())

def delete_product(product_id):
    cur = con.cursor()
    info = cur.var(cx_Oracle.STRING)
    cur.callproc('delete_product', (product_id, info))
    print(info.getvalue().capitalize())

def update_product(product_id):
    cur = con.cursor()
    info_var = cur.var(cx_Oracle.STRING)
    cur.execute('SELECT * FROM product WHERE product_id = :id', {'id':product_id})
    res = cur.fetchone()
    product_id, product_name, manufacturer, info, price, quantity = res
    price = 19.49
    cur.callproc('update_product', (product_id, product_name, manufacturer, info, price, quantity, info_var))
    print(info_var.getvalue().capitalize())

def insert_product():
    product_name, manufacturer, info, price, quantity = 'Battery', 'HAGEN', '(55 A/H), 460A L+', 40.99, 10
    cur = con.cursor()
    info_var = cur.var(cx_Oracle.STRING)
    cur.callproc('insert_product', (product_name, manufacturer, info, price, quantity, info_var))
    print(info_var.getvalue().capitalize())

def delete_client(client_id):
    cur = con.cursor()
    info = cur.var(cx_Oracle.STRING)
    cur.callproc('delete_client', (client_id, info))
    # cur.execute('delete from client where client_id = 61')
    print(info.getvalue().capitalize())

def update_client(client_id):
    cur = con.cursor()
    info = cur.var(cx_Oracle.STRING)
    cur.execute('SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT(:id))', {'id':client_id})
    res = cur.fetchone()
    client_id, f_name, s_name, birthdate, address, phone = res
    f_name = 'Elena'
    cur.callproc('update_client', (client_id, f_name, s_name, birthdate, address, phone, info))
    print(info.getvalue().capitalize())

def search_client(id, client_second_name):
    cur = con.cursor()
    cur.execute('SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT())')
    res = cur.fetchall()
    print(res)

def insert_client():
    f_name, s_name, birthdate, address, phone = 'Uladzimir', 'Putsin', datetime.datetime.strptime('7-10-1952', '%d-%m-%Y'), 'Novo-Ogarevo', 'Governmental'
    cur = con.cursor()
    info = cur.var(cx_Oracle.STRING)
    cur.callproc('INSERT_CLIENT', (f_name, s_name, birthdate, address, phone, info))
    print(info.getvalue().capitalize())

def test():
    print("Hello world")
    cur = con.cursor()
    cur.execute('select * from deals_details')
    res = cur.fetchall()
    print(res)
    cur.close()

if __name__ == "__main__":
    main()