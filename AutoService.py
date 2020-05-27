import sys
import cx_Oracle
import datetime
import hashlib
import uuid

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QLabel, QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QListWidgetItem, QTableWidgetItem
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from AutoServiceUI import Ui_MainWindow as main_Ui_MainWindow
from LoginPage import Ui_MainWindow as login_Ui_MainWindow

class LoginPage(QtWidgets.QMainWindow):
    main_window = QtCore.pyqtSignal(int, str)

    def __init__(self):
        super(LoginPage, self).__init__()
        self.setFixedSize(640, 480)
        self.ui = login_Ui_MainWindow()
        self.ui.setupUi(self)
        self.con = cx_Oracle.connect('system/Djdf1605@localhost/orcle')

        self.ui.login_btn.clicked.connect(self.login)
        self.ui.password_edit.textChanged.connect(self.clear_error)
        self.ui.firstname_line.textChanged.connect(self.clear_error)
        self.ui.lastname_line.textChanged.connect(self.clear_error)

    def clear_error(self):
        self.ui.err_label.setText('')

    def check_password(self, password):
        password, salt = password.split(':')
        return password == hashlib.sha256(salt.encode() + self.ui.password_edit.text().encode()).hexdigest()

    def login(self):
        if len(self.ui.firstname_line.text()) == 0:
            self.ui.err_label.setText('Fill in all the fields')
        elif len(self.ui.lastname_line.text()) == 0:
            self.ui.err_label.setText('Fill in all the fields')
        elif len(self.ui.password_edit.text()) == 0:
            self.ui.err_label.setText('Fill in all the fields')
        else:
            cur = self.con.cursor()
            cur.execute('SELECT * FROM employee WHERE first_name = :f_name and second_name = :s_name', \
                        {'f_name':self.ui.firstname_line.text(), 's_name':self.ui.lastname_line.text()})
            res = cur.fetchone()
            if res != None:
                id, psw, access = res[0], res[3], res[4]
                if self.check_password(psw):
                    self.main_window.emit(id, access)
                else:
                    self.ui.err_label.setText('Invalid username/password. Logon denied.')
            else:
                self.ui.err_label.setText('Invalid username/password. Logon denied.')

        
class AutoService(QtWidgets.QMainWindow):
    def __init__(self, id, access):
        super(AutoService, self).__init__()
        self.ui = main_Ui_MainWindow()
        self.ui.setupUi(self)
        self.user_id = id
        self.user_access = access
        self.con = cx_Oracle.connect('system/Djdf1605@localhost/orcle')
        self.client_is_editing = False
        self.car_is_editing = False
        self.prod_is_editing = False
        self.show_list(self.ui.listWidget, 12)
        self.show_list(self.ui.client_car_listWidget, 10)
        self.show_list(self.ui.carslistWidget, 12)
        self.show_list(self.ui.productslistWidget, 12)
        self.show_list(self.ui.dealslistWidget, 12)
        self.show_list(self.ui.deal_client_listWidget, 10)
        self.show_list(self.ui.deal_prod_listWidget, 10)
        self.show_list(self.ui.orderslistWidget, 10)
        self.show_list(self.ui.order_car_listWidget, 10)
        self.show_list(self.ui.employeeslistWidget, 12)

        self.ui.listWidget.itemSelectionChanged.connect(self.show_info)
        self.ui.carslistWidget.itemSelectionChanged.connect(self.show_info)
        self.ui.productslistWidget.itemSelectionChanged.connect(self.show_info)
        self.ui.dealslistWidget.itemSelectionChanged.connect(self.show_info)
        self.ui.orderslistWidget.itemSelectionChanged.connect(self.show_info)
        self.ui.employeeslistWidget.itemSelectionChanged.connect(self.show_info)

        self.ui.client_car_listWidget.itemSelectionChanged.connect(self.show_line)
        self.ui.deal_prod_listWidget.itemSelectionChanged.connect(self.show_line)
        self.ui.deal_client_listWidget.itemSelectionChanged.connect(self.show_line)
        self.ui.order_car_listWidget.itemSelectionChanged.connect(self.show_line)
        self.ui.close_order_btn.clicked.connect(self.close_order)
        
        
        self.ui.search_client_btn.clicked.connect(self.search)
        self.ui.search_car_btn.clicked.connect(self.search)
        self.ui.search_car_button.clicked.connect(self.search)
        self.ui.search_product_button.clicked.connect(self.search)
        self.ui.search_deal_button.clicked.connect(self.search)
        self.ui.deal_search_client_btn.clicked.connect(self.search)
        self.ui.deal_search_prod_btn.clicked.connect(self.search)
        self.ui.search_order_button.clicked.connect(self.search)
        self.ui.order_car_search_button.clicked.connect(self.search)

        self.ui.edit_product_btn.clicked.connect(self.edit)
        self.ui.edit_btn.clicked.connect(self.edit)
        self.ui.edit_car_btn.clicked.connect(self.edit)
        self.ui.edit_employee_btn.clicked.connect(self.edit)

        self.ui.add_prod_btn.clicked.connect(self.add)
        self.ui.add_btn.clicked.connect(self.add)
        self.ui.add_car_btn.clicked.connect(self.add)
        self.ui.add_deal_btn.clicked.connect(self.add)
        self.ui.add_order_button.clicked.connect(self.add)
        self.ui.add_emp_button.clicked.connect(self.add)

        self.ui.delete_btn.clicked.connect(self.delete)        
        self.ui.delete_car_btn.clicked.connect(self.delete)
        self.ui.delete_product_btn.clicked.connect(self.delete)
        self.ui.delete_employee_btn.clicked.connect(self.delete)

        self.ui.deal_client_line.textChanged.connect(self.calc_price)
        self.ui.deal_product_line.textChanged.connect(self.calc_price)
        self.ui.spinBox.valueChanged.connect(self.calc_price)

 
    ############################## OTHER ##############################
    def hash_password(self, password):
        salt = uuid.uuid4().hex
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

    def show_deals_orders(self, widget, id):
        widget.clear()
        cur = self.con.cursor()
        if widget.objectName() == 'employee_orders_list':
            cur.execute('SELECT * FROM orders where employee_id = :id', {'id':id})
        else:
            cur.execute('SELECT * FROM deal where employee_id = :id', {'id':id})
        res = cur.fetchall()
        for i in res:
            item = QtWidgets.QListWidgetItem()
            item.setFont(QtGui.QFont('Tahoma', 10))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            if widget.objectName() == 'employee_orders_list':
                item.setText(str(i[0]) + '. ' + str(i[1])+ ' ' + str(i[3]))
            else:
                item.setText(str(i[0]) + '. ' + str(i[1])+ ' ' + str(i[2]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            widget.addItem(item)

    def show_line(self):
        lines = {
            'client_car_listWidget': self.ui.car_client_id_line_2,
            'deal_prod_listWidget' : self.ui.deal_product_line,
            'deal_client_listWidget' : self.ui.deal_client_line,
            'order_car_listWidget': self.ui.new_order_car_id_line
        }
        try:
            text = self.sender().selectedItems()[0].text()
            client_id = int(text.split('.')[0])
            lines[self.sender().objectName()].setText(str(client_id))
        except:
            pass

    def calc_price(self):
        try:
            cur = self.con.cursor()
            cur.execute('SELECT price FROM product WHERE product_id = :id', \
                        {'id':self.ui.deal_product_line.text()})
            res = cur.fetchone()
            self.ui.deal_price_line_2.setText(str(round(float(res[0]) * self.ui.spinBox.value(), 2)))
        except:
            self.ui.deal_price_line_2.setText('0')

    def close_order(self):
        text = self.ui.orderslistWidget.selectedItems()[0].text()
        item_id = int(text.split('.')[0])
        buttonReply = QMessageBox.question(self, 'Confirm close', \
                    "Are you sure you want to close order {}?".format(item_id), \
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            cur = self.con.cursor()
            info = cur.var(cx_Oracle.STRING)
            cur.callproc('update_order', (item_id, info))
            self.ui.order_info_label.setText(info.getvalue().capitalize())
    
    

    ############################## DELETE ##############################
    def delete(self):
        procedures = {
            'delete_product_btn':'delete_product',
            'delete_car_btn':'delete_car',
            'delete_btn':'delete_client',
            'delete_employee_btn':'delete_employee'
        }
        labels = {
            'delete_product_btn': self.ui.prod_info_label,
            'delete_car_btn': self.ui.car_info_label,
            'delete_btn': self.ui.info_label,
            'delete_employee_btn':self.ui.emp_info_label
        }
        widgets = {
            'delete_product_btn':self.ui.productslistWidget,
            'delete_car_btn':self.ui.carslistWidget,
            'delete_btn':self.ui.listWidget,
            'delete_employee_btn':self.ui.employeeslistWidget
        }
        text = widgets[self.sender().objectName()].selectedItems()[0].text()
        item_id = int(text.split('.')[0])
        if self.user_access == 'ADMIN': 
            buttonReply = QMessageBox.question(self, 'Confirm delete', \
                        "Are you sure you want to delete item {}?".format(item_id), \
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                cur = self.con.cursor()
                info = cur.var(cx_Oracle.STRING)
                cur.callproc(procedures[self.sender().objectName()], (item_id, info))
                labels[self.sender().objectName()].setText(info.getvalue().capitalize()) 
                self.show_list(widgets[self.sender().objectName()], 12)
        else:
            labels[self.sender().objectName()].setText('Not allowed. Not enough privileges.') 




    ############################## ADD ##############################

    def add(self):
        procedures = {
            'add_prod_btn':'insert_product',
            'add_car_btn': 'insert_car',
            'add_btn': 'insert_client',
            'add_deal_btn':'insert_deal',
            'add_order_button':'insert_order',
            'add_emp_button':'insert_employee'
        }
        fields = {
            'add_prod_btn':[
                self.ui.new_prod_name_line,
                self.ui.new_prod_man_line, 
                self.ui.new_prod_info_line,
                self.ui.new_prod_price_line, 
                self.ui.new_prod_quant_line
            ],
            'add_car_btn':[
                self.ui.car_make_line_2,
                self.ui.car_model_line_2, 
                self.ui.car_year_line_2, 
                self.ui.car_vin_line_2, 
                self.ui.car_client_id_line_2
            ],
            'add_btn':[
                self.ui.f_name_line_2, 
                self.ui.s_name_line_2,
                self.ui.bd_line_2, 
                self.ui.addr_line_2, 
                self.ui.phone_line_2
            ],
            'add_deal_btn':[
                self.ui.deal_product_line,
                self.ui.spinBox,
                self.ui.deal_client_line
            ],
            'add_order_button':[
                self.ui.new_order_price_line,
                self.ui.new_order_task_line,
                self.ui.new_order_car_id_line
            ],
            'add_emp_button':[
                self.ui.new_emp_f_name_line,
                self.ui.new_emp_s_name_line,
                self.ui.new_emp_psw_line
            ]
        }
        labels = {
            'add_prod_btn': self.ui.prod_info_label,
            'add_car_btn': self.ui.car_info_label,
            'add_btn': self.ui.info_label,
            'add_deal_btn':self.ui.prod_info_label_2,
            'add_order_button':self.ui.order_info_label,
            'add_emp_button':self.ui.emp_info_label
        }
        widgets = {
            'add_prod_btn':self.ui.productslistWidget,
            'add_car_btn':self.ui.carslistWidget,
            'add_btn':self.ui.listWidget,
            'add_deal_btn':self.ui.dealslistWidget,
            'add_order_button':self.ui.orderslistWidget,
            'add_emp_button':self.ui.employeeslistWidget
        }
        if self.user_access in ['ADMIN', 'WORKER']:
            cur = self.con.cursor()
            info_var = cur.var(cx_Oracle.STRING)
            rows = [row.text() for row in fields[self.sender().objectName()] if type(row) == QLineEdit]
            if self.sender().objectName() == 'add_btn':
                rows[2] = datetime.datetime.strptime(rows[2].replace(' ', ''), '%d-%m-%Y')
            elif self.sender().objectName() == 'add_deal_btn':
                rows.insert(1, fields[self.sender().objectName()][1].value())
                rows.append(self.user_id)
            elif self.sender().objectName() == 'add_order_button':
                rows.append(self.user_id)
            elif self.sender().objectName() == 'add_emp_button':
                if self.user_access == 'ADMIN':
                    rows[2] = self.hash_password(rows[2])
                    if self.ui.admin_radioButton.isChecked():
                        rows.append('ADMIN')
                    elif self.ui.worker_radioButton.isChecked():
                        rows.append('WORKER')
                    else:
                        rows.append('READER')
                else:
                    labels[self.sender().objectName()].setText('Not allowed. Not enough privileges.')
            rows.append(info_var)
            rows = tuple(rows)
            cur.callproc(procedures[self.sender().objectName()], rows)
            labels[self.sender().objectName()].setText(info_var.getvalue().capitalize())
            if self.sender().objectName() == 'add_btn':
                self.show_list(widgets[self.sender().objectName()], 10)
            else:
                self.show_list(widgets[self.sender().objectName()], 12)
            if self.sender().objectName() == 'add_btn':
                self.show_list(self.ui.client_car_listWidget, 12)
            for row in fields[self.sender().objectName()]:
                if type(row) == QLineEdit:
                    row.setText('')
                else:
                    row.setValue(1)
        else:
            labels[self.sender().objectName()].setText('Not allowed. Not enough privileges.')


        
    ############################## EDIT ##############################

    def edit(self):
        fields = {
            'edit_product_btn':[
                self.ui.product_id_line, 
                self.ui.product_name_line, 
                self.ui.manufacturer_line, 
                self.ui.prod_info_line,
                self.ui.prod_price_line,
                self.ui.prod_quant_line
            ],
            'edit_car_btn':[
                self.ui.car_id_line,
                self.ui.car_make_line, 
                self.ui.car_model_line,
                self.ui.car_year_line,
                self.ui.car_vin_line, 
            ],
            'edit_btn':[
                self.ui.id_line, 
                self.ui.f_name_line, 
                self.ui.s_name_line,
                self.ui.bd_line,
                self.ui.addr_line,
                self.ui.phone_line
            ],
            'edit_employee_btn':[
                self.ui.emp_id_line,
                self.ui.emp_f_name_line,
                self.ui.emp_s_name_line,
                self.ui.emp_access_line
            ]
        }
        procedures = {
            'edit_product_btn':'update_product',
            'edit_car_btn':'update_car',
            'edit_btn': 'update_client',
            'edit_employee_btn':'update_employee'
        }
        labels = {
            'edit_product_btn': self.ui.prod_info_label,
            'edit_car_btn': self.ui.car_info_label,
            'edit_btn': self.ui.info_label,
            'edit_employee_btn':self.ui.emp_info_label
        }
        widgets = {
            'edit_product_btn':self.ui.productslistWidget,
            'edit_car_btn':self.ui.carslistWidget,
            'edit_btn': self.ui.listWidget,
            'edit_employee_btn':self.ui.employeeslistWidget
        }
        if self.user_access in ['ADMIN', 'WORKER']:
            cur = self.con.cursor()
            info_var = cur.var(cx_Oracle.STRING)
            rows = [row.text() for row in fields[self.sender().objectName()]]
            if self.sender().objectName() == 'edit_btn':
                    rows[3] = datetime.datetime.strptime(rows[3].replace(' ', ''), '%d-%m-%Y')
            rows.append(info_var)
            rows = tuple(rows)
            if self.sender().text() == 'SAVE':
                cur.callproc(procedures[self.sender().objectName()], rows)
                labels[self.sender().objectName()].setText(info_var.getvalue().capitalize())
                for field in fields[self.sender().objectName()][1:]:
                    field.setReadOnly(True)
                self.sender().setText('EDIT')
                self.show_list(widgets[self.sender().objectName()], 12)
            else:
                for field in fields[self.sender().objectName()][1:]:
                    field.setReadOnly(False)
                self.sender().setText('SAVE')
        else:
            labels[self.sender().objectName()].setText('Not allowed. Not enough privileges.')


    ############################## SEARCH ##############################      

    def search(self):
        widgets = {
            'search_product_button':self.ui.productslistWidget,
            'search_car_button': self.ui.carslistWidget, 
            'search_car_btn': self.ui.client_car_listWidget, 
            'search_client_btn': self.ui.listWidget,
            'search_deal_button': self.ui.dealslistWidget,
            'deal_search_prod_btn':self.ui.deal_prod_listWidget,
            'deal_search_client_btn':self.ui.deal_client_listWidget,
            'search_order_button':self.ui.orderslistWidget,
            'order_car_search_button':self.ui.order_car_listWidget
        }
        procedures = {
            'search_product_button': 'SELECT * FROM TABLE(search_product.search_product(:query))',
            'search_car_button': 'SELECT * FROM TABLE(search_car.search_car(:query))', 
            'search_car_btn': 'SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT(:id, :s_name))', 
            'search_client_btn':'SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT(:id, :s_name))',
            'search_deal_button': 'SELECT * FROM TABLE(search_deal.search_deal(:query))',
            'deal_search_prod_btn':'SELECT * FROM TABLE(search_product.search_product(:query))',
            'deal_search_client_btn':'SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT(:id, :s_name))',
            'order_car_search_button': 'SELECT * FROM TABLE(search_car.search_car(:query))'
        }
        params = {
            'search_product_button': {'query':self.ui.search_product_line.text()},
            'search_car_button': {'query':self.ui.search_car_line.text()}, 
            'search_car_btn': {'id':None, 's_name':self.ui.search_car_client.text()}, 
            'search_client_btn': {'id':None, 's_name':self.ui.lineEdit.text()},
            'search_deal_button': {'query':self.ui.search_deal_line.text()},
            'deal_search_prod_btn':{'query':self.ui.dela_search_prod_line.text()},
            'deal_search_client_btn':{'id':None, 's_name':self.ui.deal_search_client_line.text()},
            'order_car_search_button':{'query':self.ui.order_car_search_line.text()}
        }
        cur = self.con.cursor()
        if self.sender().objectName() == 'search_order_button':
            res = []
            try:
                param = datetime.datetime.strptime(self.ui.search_order_line.text(), '%d-%m-%Y')
            except:
                param = self.ui.search_order_line.text()
            queries = ['SELECT * FROM TABLE(search_order.search_order_id(:param))', 
                    'SELECT * FROM TABLE(search_order.search_order_name(:param))',
                    'SELECT * FROM TABLE(search_order.search_order_date(:param))']
            for q in queries:
                try:
                    cur.execute(q, {'param':param})
                    result = cur.fetchall()
                    for item in result:
                        res.append(item)
                except:
                    print('Error')
        else:
            cur.execute(procedures[str(self.sender().objectName())], params[str(self.sender().objectName())])
            res = cur.fetchall()
        widgets[str(self.sender().objectName())].clear()
        for i in res:
            item = QtWidgets.QListWidgetItem()
            if str(self.sender().objectName()) in [
                'search_car_btn',
                'deal_search_prod_btn', 
                'deal_search_client_btn', 
                'order_car_search_button',
                'search_order_button'
                ]:
                item.setFont(QtGui.QFont('Tahoma', 10))
            else:
                item.setFont(QtGui.QFont('Tahoma', 12))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            if self.sender().objectName() == 'search_order_button':
                item.setText(str(i[0]) + '. ' + str(i[1])+ ' ' + str(i[3][:10] + '... '))
            else:
                item.setText(str(i[0]) + '. ' + str(i[1])+ ' ' + str(i[2]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | \
                         QtCore.Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            widgets[str(self.sender().objectName())].addItem(item)



    ############################## SHOW INFO ##############################

    def show_info(self):
        list_widget = self.sender()
        fields = {
            'productslistWidget':[
                self.ui.product_id_line, 
                self.ui.product_name_line, 
                self.ui.manufacturer_line, 
                self.ui.prod_info_line,
                self.ui.prod_price_line,
                self.ui.prod_quant_line
            ],
            'listWidget':[
                self.ui.id_line,
                self.ui.f_name_line,
                self.ui.s_name_line,
                self.ui.bd_line,
                self.ui.addr_line,
                self.ui.phone_line
            ],
            'carslistWidget':[
                self.ui.car_id_line,
                self.ui.car_make_line,
                self.ui.car_model_line,
                self.ui.car_vin_line,
                self.ui.car_year_line,
                self.ui.car_client_id_line,
                self.ui.car_client_f_name_line,
                self.ui.car_client_s_name_line,
            ],
            'dealslistWidget':[
                self.ui.deal_id_line,
                self.ui.deal_date_line,
                self.ui.client_id_line,
                self.ui.cl_f_name_line,
                self.ui.cl_s_name_line,
                self.ui.prod_id_line,
                self.ui.prod_name_line,
                self.ui.deal_manufacturer_line,
                self.ui.deal_price_line,
                self.ui.deal_quant_line
            ],
            'orderslistWidget':[
                self.ui.order_id_line,
                self.ui.order_in_line,
                self.ui.order_out_line,
                self.ui.order_task,
                self.ui.order_status,
                self.ui.order_car_id,
                self.ui.order_car_make,
                self.ui.order_car_maodel,
                self.ui.order_car_vin,
                self.ui.order_client_id,
                self.ui.order_price_line
            ],
            'employeeslistWidget':[
                self.ui.emp_id_line,
                self.ui.emp_f_name_line,
                self.ui.emp_s_name_line,
                self.ui.emp_access_line
            ]
        }
        procedures = {
            'productslistWidget':'SELECT * FROM products_details WHERE product_id = :param',
            'listWidget':'SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT(:param))',
            'carslistWidget':'SELECT * FROM cars_details where car_id = :param',
            'dealslistWidget':'SELECT * FROM deals_details WHERE deal_id = :param',
            'orderslistWidget':'SELECT * FROM orders_details WHERE order_id = :param',
            'employeeslistWidget':'SELECT * FROM employees_details WHERE employee_id = :param'
        }
        try:
            text = list_widget.selectedItems()[0].text()
            item_id = int(text.split('.')[0])
            cur = self.con.cursor()
            cur.execute(procedures[self.sender().objectName()], {'param':item_id})
            if self.sender().objectName() == 'orderslistWidget':
                res = list(cur.fetchone())[:-2]
                if res[4] == 'IN PROGRESS':
                    self.ui.close_order_btn.setEnabled(True)
                else:
                    self.ui.close_order_btn.setEnabled(False)
            else:
                res = list(cur.fetchone())
            if self.sender().objectName() == 'dealslistWidget':
                res.remove(res[8])
            elif self.sender().objectName() == 'employeeslistWidget':
                res.remove(res[3])
                self.show_deals_orders(self.ui.employee_orders_list, item_id)
                self.show_deals_orders(self.ui.employee_deals_list, item_id)
            for i in range(len(res)):
                if type(res[i]) == datetime.datetime:
                    fields[self.sender().objectName()][i].setText(res[i].strftime("%d-%m-%Y "))
                else:
                    fields[self.sender().objectName()][i].setText(str(res[i]))
        except:
            for i in range(len(fields[self.sender().objectName()])):
                fields[self.sender().objectName()][i].setText('')



    ############################## SHOW LIST ##############################

    def show_list(self, widget, fs):
        procedures = {
            'productslistWidget':'SELECT * FROM TABLE(search_product.search_product())',
            'listWidget':'SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT())',
            'client_car_listWidget':'SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT())',
            'carslistWidget':'SELECT * FROM TABLE(search_car.search_car())',
            'dealslistWidget':'SELECT * FROM TABLE(search_deal.search_deal())',
            'deal_client_listWidget':'SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT())',
            'deal_prod_listWidget':'SELECT * FROM TABLE(search_product.search_product())',
            'orderslistWidget':'SELECT * FROM TABLE(search_order.search_order_all())',
            'order_car_listWidget':'SELECT * FROM TABLE(search_car.search_car())',
        }
        widget.clear()
        cur = self.con.cursor()
        if widget.objectName() == 'employeeslistWidget':
            cur.execute('SELECT * FROM employees_details')
        else:
            cur.execute(procedures[str(widget.objectName())])
        res = cur.fetchall()
        for i in res:
            item = QtWidgets.QListWidgetItem()
            item.setFont(QtGui.QFont('Tahoma', fs))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            if widget.objectName() == 'orderslistWidget':
                item.setText(str(i[0]) + '. ' + str(i[1]) + ' ' + str(i[3][:10]) + '... ') 
            else:
                item.setText(str(i[0]) + '. ' + str(i[1])+ ' ' + str(i[2]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            widget.addItem(item)


class Controller:
    
    def __init__(self):
        pass

    def show_login(self):
        self.login = LoginPage()
        self.login.show()
        self.login.main_window.connect(self.show_main)
    
    def show_main(self, id, access):
        self.main = AutoService(id, access)
        self.login.close()
        self.main.show()


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    print('Hello world!')
    controller = Controller()
    controller.show_login()
    sys.exit(app.exec_())
        

if __name__ == '__main__':
    main()