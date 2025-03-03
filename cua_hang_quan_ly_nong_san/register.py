import sys
import os
import hashlib
import mysql.connector
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget
from PySide6.QtCore import Qt, QSize

#from login import LoginDialog  # Removed to prevent circular import

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="quan_ly_nong_san"
    )

class RegisterDialog(QDialog):
    def __init__(self, login_window=None):  # login_window can be None
        super().__init__()
        self.login_window = login_window  # Reference to the login window (can be None)
        self.setWindowTitle("Đăng Ký")
        self.setGeometry(500, 200, 900, 450)  # Widened window for better balance

        #Main Layout
        main_layout = QtWidgets.QHBoxLayout(self)

        #Left Layout (Image)
        left_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(left_layout, 5)  # Give image section 5/10 of the width

        self.image_label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap("anh.jpg") #Replace this
        self.image_label.setPixmap(pixmap.scaled(QSize(450, 400), Qt.AspectRatioMode.KeepAspectRatio)) #Resize biger
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.image_label)

        #Right Layout (Form)
        right_layout = QtWidgets.QVBoxLayout() #Use QFrom layout for align.
        main_layout.addLayout(right_layout, 5) # Give form section also 5/10 of the width
        right_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter) #Center from layout

        #Title:
        self.label_title = QtWidgets.QLabel("ĐĂNG KÝ TÀI KHOẢN", self)
        font = QtGui.QFont("Arial", 14)  # Corrected font definition
        font.setBold(True)
        self.label_title.setFont(font)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Corrected alignment
        right_layout.addWidget(self.label_title)

        #Name
        self.name = QtWidgets.QLineEdit(self)
        self.name.setPlaceholderText("Tên đăng nhập")
        self.name.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                border: 2px solid #85929E;
                background-color: #EAF2F8;
                color: #2C3E50;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        right_layout.addWidget(self.name)

        #Email
        self.email = QtWidgets.QLineEdit(self)
        self.email.setPlaceholderText("Email")
        self.email.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                border: 2px solid #85929E;
                background-color: #EAF2F8;
                color: #2C3E50;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        right_layout.addWidget(self.email)

        #Password
        self.passw = QtWidgets.QLineEdit(self)
        self.passw.setPlaceholderText("Mật khẩu")
        self.passw.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.passw.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                border: 2px solid #85929E;
                background-color: #EAF2F8;
                color: #2C3E50;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        right_layout.addWidget(self.passw)

        #Register Buttons
        self.btnregister = QtWidgets.QPushButton("Đăng Ký", self)
        self.btnregister.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btnregister.clicked.connect(self.register_user)  # Ensure this method exists
        right_layout.addWidget(self.btnregister)

        #Login
        self.btnlogin = QtWidgets.QPushButton("Đăng Nhập", self)
        self.btnlogin.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btnlogin.clicked.connect(self.switch_to_login)
        right_layout.addWidget(self.btnlogin)

        #Styling main
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f8ea;
                border-radius: 10px;
            }
            QLabel {
                color: #333333;
            }
        """)

    def register_user(self):
        username = self.name.text().strip()
        password = self.passw.text().strip()
        email = self.email.text().strip()

        if not username or not password or not email:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Check if the username or email already exists
            cursor.execute("SELECT * FROM tai_khoan WHERE ten_tk = %s OR email = %s", (username, email))
            if cursor.fetchone():
                QMessageBox.warning(self, "Lỗi", "Tài khoản hoặc email đã tồn tại!")
                return

            # Hash the password before saving
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Add the account to the database
            sql = "INSERT INTO tai_khoan (ten_tk, mk_tk, email) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, hashed_password, email))
            conn.commit()

            QMessageBox.information(self, "Thành công", "Đăng ký thành công! Hãy đăng nhập.")
            self.switch_to_login()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi đăng ký: {err}")

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def switch_to_login(self):
         self.close()
         if self.login_window:  # Check if login_window is valid
            self.login_window.show()
         else:
            from login import LoginDialog #Import inside this function only when needed.
            self.login_window = LoginDialog()
            self.login_window.show() #Show the login window.

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #register_dialog = RegisterDialog(LoginDialog())  # Pass reference to the login window
    register_dialog = RegisterDialog() #Removed LoginDialog() instantiation here to solve the circular dependency
    register_dialog.show()
    sys.exit(app.exec())