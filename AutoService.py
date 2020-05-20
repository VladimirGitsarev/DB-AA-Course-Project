import sys
import cx_Oracle
import datetime

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QLabel, QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QListWidgetItem, QTableWidgetItem
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from AutoServiceUI import Ui_MainWindow

class AutoService(QtWidgets.QMainWindow):
    def __init__(self):
        super(AutoService, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.con = cx_Oracle.connect('system/Djdf1605@localhost/orcle')
        self.client_is_editing = False
        self.car_is_editing = False
        self.show_clients(self.ui.listWidget, 12)
        self.show_clients(self.ui.client_car_listWidget, 10)
        self.show_cars()

        self.ui.listWidget.itemSelectionChanged.connect(self.show_client_info)
        self.ui.carslistWidget.itemSelectionChanged.connect(self.show_cars_info)
        self.ui.client_car_listWidget.itemSelectionChanged.connect(self.show_client_car_id)
        self.ui.search_client_btn.clicked.connect(self.search_client)
        self.ui.search_car_btn.clicked.connect(self.search_car_client)
        self.ui.edit_btn.clicked.connect(self.edit_client)
        self.ui.add_btn.clicked.connect(self.add_client)
        self.ui.delete_btn.clicked.connect(self.delete_client)
        self.ui.edit_car_btn.clicked.connect(self.edit_car)
        self.ui.add_car_btn.clicked.connect(self.add_car)
        self.ui.delete_car_btn.clicked.connect(self.delete_car)

 
    ############################## OTHER ##############################
    def show_client_car_id(self):
        try:
            text = self.ui.client_car_listWidget.selectedItems()[0].text()
            client_id = int(text.split('.')[0])
            self.ui.car_client_id_line_2.setText(str(client_id))
        except:
            pass
    

    ############################## DELETE ##############################
    def delete_car(self):
        text = self.ui.carslistWidget.selectedItems()[0].text()
        car_id = int(text.split('.')[0])
        buttonReply = QMessageBox.question(self, 'Confirm delete', \
                    "Are you sure you want to delete car {} ?".format(car_id), \
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            cur = self.con.cursor()
            info = cur.var(cx_Oracle.STRING)
            cur.callproc('delete_car', (car_id, info))
            self.ui.car_info_label.setText(info.getvalue().capitalize()) 

    def delete_client(self):
        text = self.ui.listWidget.selectedItems()[0].text()
        client_id = int(text.split('.')[0])
        buttonReply = QMessageBox.question(self, 'Confirm delete', \
                    "Are you sure you want to delete client {} ?".format(client_id), \
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            cur = self.con.cursor()
            info = cur.var(cx_Oracle.STRING)
            cur.callproc('delete_client', (client_id, info))
            self.ui.info_label.setText(info.getvalue().capitalize())
            self.show_clients(self.ui.listWidget, 12)
            self.show_cars()



    ############################## ADD ##############################

    def add_car(self):
        make, model, year, vin, client_id = self.ui.car_make_line_2.text(),\
        self.ui.car_model_line_2.text(), self.ui.car_year_line_2.text(), \
        self.ui.car_vin_line_2.text(), self.ui.car_client_id_line_2.text()
        cur = self.con.cursor()
        info = cur.var(cx_Oracle.STRING)
        cur.callproc('insert_car', (make, model, year, vin, client_id, info))
        self.ui.car_info_label.setText(info.getvalue().capitalize()) 
        self.ui.car_make_line_2.setText('')
        self.ui.car_model_line_2.setText('')
        self.ui.car_year_line_2.setText('')
        self.ui.car_vin_line_2.setText('')
        self.ui.car_client_id_line_2.setText('')
        self.show_cars()

    def add_client(self):
        f_name, s_name, birthdate, address, phone = \
            self.ui.f_name_line_2.text(), self.ui.s_name_line_2.text(), \
            self.ui.bd_line_2.text(), self.ui.addr_line_2.text(), self.ui.phone_line_2.text()
        cur = self.con.cursor()
        info = cur.var(cx_Oracle.STRING)
        cur.callproc('insert_client', (f_name, s_name, datetime.datetime.strptime(\
                    birthdate.replace(' ', ''), '%d-%m-%Y'), address, phone, info))
        self.ui.info_label.setText(info.getvalue().capitalize())
        self.show_clients(self.ui.listWidget, 12)
        self.ui.f_name_line_2.setText('') 
        self.ui.s_name_line_2.setText('')
        self.ui.bd_line_2.setText('')
        self.ui.addr_line_2.setText('')
        self.ui.phone_line_2.setText('')


        
    ############################## EDIT ##############################

    def edit_car(self):
        if self.car_is_editing:
            cur = self.con.cursor()
            info_var = cur.var(cx_Oracle.STRING)
            car_id, make, model, vin, year = self.ui.car_id_line.text(), \
            self.ui.car_make_line.text(), self.ui.car_model_line.text(), \
            self.ui.car_vin_line.text(), self.ui.car_year_line.text()
            cur.callproc('update_car', (car_id, make, model, year, vin, info_var))
            self.ui.car_info_label.setText(info_var.getvalue().capitalize()) 
            self.ui.car_make_line.setReadOnly(True)
            self.ui.car_model_line.setReadOnly(True)
            self.ui.car_vin_line.setReadOnly(True)
            self.ui.car_year_line.setReadOnly(True)
            self.ui.edit_car_btn.setText('EDIT')
            self.car_is_editing = False   
            self.show_cars()
        else:            
            self.ui.car_make_line.setReadOnly(False)
            self.ui.car_model_line.setReadOnly(False)
            self.ui.car_vin_line.setReadOnly(False)
            self.ui.car_year_line.setReadOnly(False)
            self.ui.edit_car_btn.setText('SAVE')
            self.car_is_editing = True 
            
    def edit_client(self):
        if self.client_is_editing:
            client_id, f_name, s_name, birthdate, address, phone = \
            self.ui.id_line.text(), self.ui.f_name_line.text(), self.ui.s_name_line.text(), \
            self.ui.bd_line.text(), self.ui.addr_line.text(), self.ui.phone_line.text()
            cur = self.con.cursor()
            info = cur.var(cx_Oracle.STRING)
            cur.callproc('update_client', (client_id, f_name, s_name,  \
                        datetime.datetime.strptime(birthdate.replace(' ', ''), '%d-%m-%Y'), address, phone, info))
            self.ui.info_label.setText(info.getvalue().capitalize())
            self.ui.f_name_line.setReadOnly(True)
            self.ui.s_name_line.setReadOnly(True)
            self.ui.bd_line.setReadOnly(True)
            self.ui.addr_line.setReadOnly(True)
            self.ui.phone_line.setReadOnly(True)
            self.ui.edit_btn.setText('EDIT')
            self.client_is_editing = False
        else:
            self.ui.f_name_line.setReadOnly(False)
            self.ui.s_name_line.setReadOnly(False)
            self.ui.bd_line.setReadOnly(False)
            self.ui.addr_line.setReadOnly(False)
            self.ui.phone_line.setReadOnly(False)
            self.ui.edit_btn.setText('SAVE')
            self.client_is_editing = True



    ############################## SEARCH ##############################        

    def search_car_client(self):
        cur = self.con.cursor()
        cur.execute('SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT(:id, :s_name))', \
                   {'id':None, 's_name':self.ui.search_car_client.text()})
        res = cur.fetchall()
        self.ui.client_car_listWidget.clear()
        for client in res:
            item = QtWidgets.QListWidgetItem()
            item.setFont(QtGui.QFont('Tahoma', 10))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            item.setText(str(client[0]) + '. ' + str(client[1])+ ' ' + str(client[2]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | \
                         QtCore.Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.ui.client_car_listWidget.addItem(item)

    def search_client(self):
        cur = self.con.cursor()
        cur.execute('SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT(:id, :s_name))', \
                   {'id':None, 's_name':self.ui.lineEdit.text()})
        res = cur.fetchall()
        self.ui.listWidget.clear()
        for client in res:
            item = QtWidgets.QListWidgetItem()
            item.setFont(QtGui.QFont('Tahoma', 12))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            item.setText(str(client[0]) + '. ' + str(client[1])+ ' ' + str(client[2]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | \
                         QtCore.Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.ui.listWidget.addItem(item)



    ############################## SHOW INFO ##############################

    def show_cars_info(self):
        try:
            text = self.ui.carslistWidget.selectedItems()[0].text()
            car_id = int(text.split('.')[0])
            cur = self.con.cursor()
            cur.execute('SELECT * FROM cars_details where car_id = :id', {'id':car_id})
            car_id, make, model, vin, year, c_id, c_f_name, c_s_name = cur.fetchone()
            self.ui.car_id_line.setText(str(car_id))
            self.ui.car_make_line.setText(make)
            self.ui.car_model_line.setText(model)
            self.ui.car_vin_line.setText(vin)
            self.ui.car_year_line.setText(str(year))
            self.ui.car_client_id_line.setText(str(c_id))
            self.ui.car_client_f_name_line.setText(c_f_name)
            self.ui.car_client_s_name_line.setText(c_s_name)
        except:
            self.ui.car_id_line.setText('')
            self.ui.car_make_line.setText('')
            self.ui.car_model_line.setText('')
            self.ui.car_vin_line.setText('')
            self.ui.car_year_line.setText('')
            self.ui.car_client_id_line.setText('')
            self.ui.car_client_f_name_line.setText('')
            self.ui.car_client_s_name_line.setText('')

    def show_client_info(self):
        try:
            text = self.ui.listWidget.selectedItems()[0].text()
            client_id = int(text.split('.')[0])
            cur = self.con.cursor()
            cur.execute('SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT(:id))', {'id':client_id})
            id, f_name, s_name, date, address, phone = cur.fetchone()
            self.ui.id_line.setText(str(id))
            self.ui.f_name_line.setText(f_name)
            self.ui.s_name_line.setText(s_name)
            self.ui.bd_line.setText(date.strftime("%d-%m-%Y "))
            self.ui.addr_line.setText(address)
            self.ui.phone_line.setText(phone)
        except:
            self.ui.id_line.setText('')
            self.ui.f_name_line.setText('')
            self.ui.s_name_line.setText('')
            self.ui.bd_line.setText('')
            self.ui.addr_line.setText('')
            self.ui.phone_line.setText('')



    ############################## SHOW ##############################

    def show_cars(self):
        self.ui.carslistWidget.clear()
        cur = self.con.cursor()
        cur.execute('SELECT * FROM cars_details')
        res = cur.fetchall()
        for car in res:
            item = QtWidgets.QListWidgetItem()
            item.setFont(QtGui.QFont('Tahoma', 12))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            item.setText(str(car[0]) + '. ' + str(car[1])+ ' ' + str(car[2]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            self.ui.carslistWidget.addItem(item)

    def show_clients(self, widget, fs):
        widget.clear()
        cur = self.con.cursor()
        cur.execute('SELECT * FROM TABLE(SEARCH_CLIENT.SEARCH_CLIENT())')
        res = cur.fetchall()
        for client in res:
            item = QtWidgets.QListWidgetItem()
            item.setFont(QtGui.QFont('Tahoma', fs))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            item.setText(str(client[0]) + '. ' + str(client[1])+ ' ' + str(client[2]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            widget.addItem(item)

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    
    autoservice = AutoService()
    autoservice.show()
    sys.exit(app.exec_())
        

if __name__ == '__main__':
    main()