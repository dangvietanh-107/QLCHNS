import sys
import mysql.connector
import hashlib
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtCore import Qt, QSize
from main import MenuApp  # Assuming main.py is in the same directory

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="quan_ly_nong_san"
    )

class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng Nhập")
        self.setGeometry(500, 200, 900, 450)  # Widened window for better balance

        #Main Layout
        main_layout = QtWidgets.QHBoxLayout(self)

        #Left Layout (Image)
        left_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(left_layout, 5)  # Give image section 5/10 of the width

        self.image_label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap("anh.jpg")
        self.image_label.setPixmap(pixmap.scaled(QSize(450, 400), Qt.AspectRatioMode.KeepAspectRatio)) #Resize biger
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.image_label)

        #Right Layout (Form)
        right_layout = QtWidgets.QVBoxLayout() #Use QFrom layout for align.
        main_layout.addLayout(right_layout, 5) # Give form section also 5/10 of the width
        right_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter) #Center from layout

        #Title:
        self.label_title = QtWidgets.QLabel("CỬA HÀNG QUẢN LÝ NÔNG SẢN", self)
        font = QtGui.QFont("Arial", 14)  # Corrected font definition
        font.setBold(True)
        self.label_title.setFont(font)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Corrected alignment
        right_layout.addWidget(self.label_title)

        #Username
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

        #Login Buttons
        self.btnlogin = QtWidgets.QPushButton("Đăng Nhập", self)
        self.btnlogin.setStyleSheet("""
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
        self.btnlogin.clicked.connect(self.login_user)  # Kết nối với phương thức login_user
        right_layout.addWidget(self.btnlogin)

        #Register Buttons
        self.btnregister = QtWidgets.QPushButton("Đăng Ký", self)
        self.btnregister.setStyleSheet("""
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
        self.btnregister.clicked.connect(self.switch_to_register)
        right_layout.addWidget(self.btnregister)

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

    def login_user(self):
        username = self.name.text().strip()
        password = self.passw.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Mã hóa mật khẩu nhập vào để so sánh với DB
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Truy vấn kiểm tra tài khoản và mật khẩu
            cursor.execute("SELECT * FROM tai_khoan WHERE ten_tk = %s AND mk_tk = %s", (username, hashed_password))
            user = cursor.fetchone()

            if user:
                QMessageBox.information(self, "Thành công", "Đăng nhập thành công!")
                self.open_main_window()
            else:
                QMessageBox.warning(self, "Lỗi", "Sai tài khoản hoặc mật khẩu!")

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {err}")

        finally:
            if conn and conn.is_connected():  # Check if conn exists
                cursor.close()
                conn.close()
                

    def open_main_window(self):
        print("Mở cửa sổ chính")
        self.main_window = MenuApp()  # Create MenuApp instance
        self.main_window.show()
        self.close()


    def switch_to_register(self):
        from register import RegisterDialog # Avoid circular import
        self.register_dialog = RegisterDialog(self)
        self.register_dialog.show()
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_dialog = LoginDialog()
    login_dialog.show()
    sys.exit(app.exec())