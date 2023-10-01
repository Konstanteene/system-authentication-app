import re
import sqlite3
import sys

from PyQt5 import QtWidgets

import modules.add_user
import modules.admin_window
import modules.change_password
import modules.first_start_window
import modules.info
import modules.user_window


class StartWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(StartWindow, self).__init__()
        self.ui = modules.first_start_window.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.login_btn.clicked.connect(self.start)
        self.ui.pushButton.clicked.connect(self.info)
        self.ui.exit.clicked.connect(self.close)
        self.count_error = 0

    def start(self):
        login = self.ui.login.text()
        password = self.ui.password.text()
        with sqlite3.connect('logs.db') as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM user_password")
            for i in cur.fetchall():
                if login == i[0] and password == i[1] and login == 'ADMIN' and login != 0 and password != 0:
                    print("ADMIN WINDOW")
                    self.ui.a = AdminWindow()
                    self.ui.a.show()
                    break
                elif login == i[0] and password == i[1] and i[2] != 1 and login != 0 and password != 0:
                    print("USER WINDOW")
                    self.ui.a = UserWindow(login)
                    self.ui.a.show()
                    self.ui.error.setText("")
                    break
                elif login == i[0] and password == i[1] and i[2] == 1 and login != 0 and password != 0:
                    print('Blocked user')
                    self.ui.error.setText('Blocked user')
                    break
                else:
                    self.ui.error.setText(f"INCORRECT LOGIN OR PASSWORD\n You have {3 - self.count_error} tries ")
                    print(self.count_error)
                    if 3 - self.count_error == 0:
                        self.ui.login_btn.clicked.connect(self.close)
            self.count_error += 1

    def info(self):
        self.ui.a = InfoWindow()
        self.ui.a.show()


class AdminWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super(AdminWindow, self).__init__()
            self.ui = modules.admin_window.Ui_MainWindow()
            self.ui.setupUi(self)
            self.ui.change_pass.clicked.connect(self.change_pass)
            self.ui.add_user.clicked.connect(self.add_user)
            self.ui.block_user.clicked.connect(self.block_user)
            self.ui.unblock_user.clicked.connect(self.unblock_user)
            self.ui.spec_pass_on.clicked.connect(self.special_password_on)
            self.ui.spec_pass_off.clicked.connect(self.special_password_off)
            self.ui.exit.clicked.connect(self.close)
            self.ui.refresh.clicked.connect(self.refresh)
            self.show_all_user()
            self.info_window()
            self.show()

        def change_pass(self):
            self.ui.a = ChangePassword('ADMIN')
            self.ui.a.show()
            self.info_window()

        def show_all_user(self):
            with sqlite3.connect('logs.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM user_password")
                self.ui.comboBox.clear()
                for row in cur.fetchall():
                    self.ui.comboBox.addItem(row[0])
                self.info_window()

        def add_user(self):
            self.ui.a = AddUser()
            self.ui.a.show()
            self.info_window()

        def block_user(self):
            user = str(self.ui.comboBox.currentText())
            # print(user)
            with sqlite3.connect('logs.db') as conn:
                cur = conn.cursor()
                if user != 'ADMIN':
                    self.info_window()
                    cur.execute(f"UPDATE user_password SET block_status=1 WHERE login='{user}'")
                    self.info_window()
                else:
                    self.ui.error.setText("You can't do it with ADMIN")

        def unblock_user(self):
            user = str(self.ui.comboBox.currentText())
            # print(user)
            with sqlite3.connect('logs.db') as conn:
                cur = conn.cursor()
                if user != 'ADMIN':
                    self.info_window()
                    cur.execute(f"UPDATE user_password SET block_status=0 WHERE login='{user}'")
                    self.info_window()
                else:
                    self.ui.error.setText("You can't do it with ADMIN")

        def info_window(self):
            with sqlite3.connect('logs.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM user_password")

            row = 0
            self.ui.tableWidget.setRowCount(len(cur.fetchall()))
            cur.execute("SELECT * FROM user_password")
            for i in cur.fetchall():
                self.ui.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(i[0]))
                self.ui.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(i[1]))
                self.ui.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(i[2])))
                self.ui.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(i[3])))
                row = row + 1

        def special_password_on(self):
            user = str(self.ui.comboBox.currentText())
            with sqlite3.connect('logs.db') as conn:
                cur = conn.cursor()
                if user != 'ADMIN':
                    self.ui.radioButton.setChecked(True)
                    self.info_window()
                    cur.execute(f"UPDATE user_password SET special_password=1 WHERE login='{user}'")
                else:
                    self.ui.error.setText("You can't do it with ADMIN")

        def special_password_off(self):
            user = str(self.ui.comboBox.currentText())
            with sqlite3.connect('logs.db') as conn:
                cur = conn.cursor()
                if user != 'ADMIN':
                    self.ui.radioButton.setChecked(False)
                    self.info_window()
                    cur.execute(f"UPDATE user_password SET special_password=0 WHERE login='{user}'")
                else:
                    self.ui.error.setText("You can't do it with ADMIN")

        def refresh(self):
            self.info_window()
            self.show_all_user()


class UserWindow(QtWidgets.QMainWindow):
    def __init__(self, login):
        super(UserWindow, self).__init__()
        self.ui = modules.user_window.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.ChangePassword.clicked.connect(self.change_pass)
        self.ui.pushButton.clicked.connect(self.close)
        self.login = login

    def change_pass(self):
        self.ui.a = ChangePassword(self.login)
        self.ui.a.show()


class ChangePassword(QtWidgets.QDialog):
    def __init__(self, login):
        super(ChangePassword, self).__init__()
        self.ui = modules.change_password.Ui_Dialog()
        self.ui.setupUi(self)
        self.login = login
        self.ui.btn.clicked.connect(self.change_pass)

    def change_pass(self):
        # login = 'ADMIN'
        old_pass = self.ui.old_password.text()
        new_pass = self.ui.new_password.text()
        if len(old_pass) == 0 or len(new_pass) == 0:
            self.ui.error.setText('Fill login gap pls')
        else:
            with sqlite3.connect('logs.db') as conn:
                cur = conn.cursor()
                statement = f"SELECT login, password, special_password from user_password WHERE login='{self.login}';"
                cur.execute(statement)
            if cur.fetchone()[1] != old_pass:
                self.ui.error.setText("Incorrect password")
            else:
                cur.execute(statement)
                if cur.fetchone()[2] == 1:
                    if re.search("[A-Za-z0-9А-Яа-я]", new_pass):
                        with sqlite3.connect('logs.db') as conn:
                            self.ui.error.setText('password changed')
                            cur = conn.cursor()
                            cur.execute(f"UPDATE user_password SET password='{new_pass}' WHERE login='{self.login}'")
                            AdminWindow().info_window()
                    else:
                        self.ui.error.setText("Password must contain A-Z, А-Я, 0-9")
                else:
                    with sqlite3.connect('logs.db') as conn:
                        print('password changed')
                        self.ui.error.setText('password changed')
                        cur = conn.cursor()
                        cur.execute(f"UPDATE user_password SET password='{new_pass}' WHERE login='{self.login}'")
                        AdminWindow().info_window()
            conn.close()


class AddUser(QtWidgets.QDialog):
    def __init__(self):
        super(AddUser, self).__init__()
        self.ui = modules.add_user.Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.btn.clicked.connect(self.add_user)
        self.ui.btn_2.clicked.connect(self.close)

    def add_user(self):
        usern = self.ui.username.text()
        with sqlite3.connect('logs.db') as conn:
            cur = conn.cursor()
            statement = f"SELECT login FROM user_password WHERE login='{usern}';"
            cur.execute(statement)
            if cur.fetchone() is None and len(usern) != 0:
                cur.execute(f"INSERT INTO user_password (login, password, block_status, special_password) VALUES ('{usern}','{usern}', 0, 0)")
                self.ui.error.setText(f"User added with default password '{usern}'")
                self.ui.btn.clicked.connect(self.close)
                self.ui.a = StartWindow()
                self.ui.a.show()
            if len(usern) == 0:
                self.ui.error.setText('Fill in the field')
            else:
                self.ui.error.setText('Such username exists')


class InfoWindow(QtWidgets.QDialog):
    def __init__(self):
        super(InfoWindow, self).__init__()
        self.ui = modules.info.Ui_dsad()
        self.ui.setupUi(self)


# main
with sqlite3.connect('logs.db') as conn:
    cur = conn.cursor()
    try:
        cur.execute(
            'CREATE TABLE IF NOT EXISTS user_password ("login" TEXT NOT NULL UNIQUE, "password" TEXT, '
            '"block_status" INTEGER NOT NULL DEFAULT 0, "special_password" INTEGER NOT NULL DEFAULT 0)')
        cur.execute('INSERT INTO user_password (login, password) VALUES ("ADMIN","ADMIN")')
    except:
        pass

app = QtWidgets.QApplication(sys.argv)
a = StartWindow()
a.show()
sys.exit(app.exec())


