import sys
import mysql.connector
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog
from PySide6.QtCore import QFile, QIODevice, Qt
from PySide6.QtUiTools import QUiLoader
import re
import openpyxl

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "quan_ly_nong_san"
}

class UserManagement(QtWidgets.QWidget):
    customer_added = QtCore.Signal()  # Define a signal

    def __init__(self):
        super().__init__()
        uifile = QFile("users.ui")
        if not uifile.open(QIODevice.ReadOnly):
            print(f"Cannot open {uifile.fileName()}: {uifile.errorString()}")
            sys.exit(-1)

        loader = QUiLoader()
        self.ui = loader.load(uifile, self)
        uifile.close()

        if self.ui is None:
            print(loader.errorString())
            sys.exit(-1)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.ui.centralwidget)

        self.ui.btnSearch.clicked.connect(self.search_customers)
        self.ui.btnAdd.clicked.connect(self.add_customer)
        self.ui.btnEdit.clicked.connect(self.edit_customer)
        self.ui.btnDelete.clicked.connect(self.delete_customer)
        self.ui.btnClear.clicked.connect(self.clear_inputs)
        self.ui.btnExport.clicked.connect(self.export_excel)
        self.setup_table()
        self.load_customers()

        self.ui.tableKhachHang.itemClicked.connect(self.display_customer_info)

    def connect_db(self):
        """Connect to the MySQL database."""
        return mysql.connector.connect(**DB_CONFIG)

    def setup_table(self):
        """Set up the QTableWidget headers."""
        self.ui.tableKhachHang.setColumnCount(3)
        self.ui.tableKhachHang.setHorizontalHeaderLabels(["Mã KH", "Tên KH", "Email"])
        header = self.ui.tableKhachHang.horizontalHeader()
        for col in range(self.ui.tableKhachHang.columnCount()):
            header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.ui.tableKhachHang.setStyleSheet("QTableWidget::item { text-align: center; }")

    def load_customers(self):
        """Load customers from the database into the table."""
        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql = "SELECT ma_kh, ten_kh, email FROM khach_hang"
            cursor.execute(sql)
            customers = cursor.fetchall()

            self.ui.tableKhachHang.setRowCount(len(customers))
            for row, customer in enumerate(customers):
                self.ui.tableKhachHang.setItem(row, 0, QTableWidgetItem(str(customer[0])))
                self.ui.tableKhachHang.setItem(row, 1, QTableWidgetItem(customer[1]))
                self.ui.tableKhachHang.setItem(row, 2, QTableWidgetItem(customer[2]))

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def search_customers(self):
        """Search for customers based on the search term."""
        keyword = self.ui.txtSearch.text().strip()
        if not keyword:
            self.load_customers()
            return
        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql = """SELECT ma_kh, ten_kh, email
                     FROM khach_hang
                     WHERE (ma_kh LIKE %s
                        OR ten_kh LIKE %s
                        OR email LIKE %s)"""

            value = ('%' + keyword + '%',)*3
            cursor.execute(sql, value)
            customers = cursor.fetchall()

            if not customers:
                QMessageBox.information(self, "Thông báo", "Không tìm thấy khách hàng với thông tin này.")
                self.load_customers()
                return

            self.ui.tableKhachHang.setRowCount(len(customers))
            for row, customer in enumerate(customers):
                self.ui.tableKhachHang.setItem(row, 0, QTableWidgetItem(str(customer[0])))
                self.ui.tableKhachHang.setItem(row, 1, QTableWidgetItem(customer[1]))
                self.ui.tableKhachHang.setItem(row, 2, QTableWidgetItem(customer[2]))

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def add_customer(self):
        """Add a new customer to the database."""
        ma_kh = self.ui.txtMaKH.text().strip()
        ten_kh = self.ui.txtTenKH.text().strip()
        email = self.ui.txtEmail.text().strip()

        if not (ma_kh and ten_kh and email):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return
        if not re.match(r"[^@]+@gmail\.com", email):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đúng định dạng email (@gmail.com).")
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql_check = "SELECT ma_kh FROM khach_hang WHERE ma_kh = %s"
            cursor.execute(sql_check, (ma_kh,))
            result = cursor.fetchone()
            if result:
                QMessageBox.warning(self, "Lỗi", "Mã khách hàng đã tồn tại.")
                return

            sql = """INSERT INTO khach_hang (ma_kh, ten_kh, email)
                     VALUES (%s, %s, %s)"""
            values = (ma_kh, ten_kh, email)
            cursor.execute(sql, values)
            conn.commit()

            QMessageBox.information(self, "Thành công", "Thêm khách hàng thành công!")
            self.load_customers()
            self.clear_inputs()
            self.customer_added.emit() # Emit signal after successful add

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def edit_customer(self):
        """Edit an existing customer in the database."""
        ma_kh = self.ui.txtMaKH.text().strip()
        ten_kh = self.ui.txtTenKH.text().strip()
        email = self.ui.txtEmail.text().strip()

        if not ma_kh:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã khách hàng để sửa.")
            return

        if not re.match(r"[^@]+@gmail\.com", email):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đúng định dạng email (@gmail.com).")
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql = """UPDATE khach_hang
                     SET ten_kh = %s, email = %s
                     WHERE ma_kh = %s"""
            values = (ten_kh, email, ma_kh)
            cursor.execute(sql, values)
            conn.commit()

            if cursor.rowcount == 0:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy khách hàng để sửa.")
                return

            QMessageBox.information(self, "Thành công", "Sửa khách hàng thành công!")
            self.load_customers()
            self.clear_inputs()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def delete_customer(self):
        """Delete a customer from the database."""
        ma_kh = self.ui.txtMaKH.text().strip()
        if not ma_kh:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã khách hàng để xóa.")
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql = "DELETE FROM khach_hang WHERE ma_kh = %s"
            cursor.execute(sql, (ma_kh,))
            conn.commit()
            if cursor.rowcount == 0:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy khách hàng để xóa.")
                return

            QMessageBox.information(self, "Thành công", "Xóa khách hàng thành công!")
            self.load_customers()
            self.clear_inputs()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def clear_inputs(self):
        """Clear the input fields."""
        self.ui.txtMaKH.clear()
        self.ui.txtTenKH.clear()
        self.ui.txtEmail.clear()

    def export_excel(self):
        """Export data from the table to an Excel file."""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Chọn đường dẫn để lưu", "", "Excel Files (*.xlsx)", options=options)

        if filename:
            try:
                conn = self.connect_db()
                cursor = conn.cursor()

                sql = "SELECT ma_kh, ten_kh, email FROM khach_hang"
                cursor.execute(sql)
                customers = cursor.fetchall()

                if not customers:
                    QMessageBox.warning(self, "Lỗi", "Không có dữ liệu để xuất.")
                    return

                workbook = openpyxl.Workbook()
                sheet = workbook.active

                headers = ["Mã KH", "Tên KH", "Email"]
                sheet.append(headers)

                for customer in customers:
                    sheet.append(customer)

                workbook.save(filename)
                QMessageBox.information(self, "Thành công", f"Dữ liệu đã được xuất ra file {filename}.")

            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi xuất Excel: {e}")
            finally:
                if conn and conn.is_connected():
                    cursor.close()
                    conn.close()

    def display_customer_info(self, item):
        """Display customer information in the input fields when a row is clicked."""
        row = item.row()

        ma_kh = self.ui.tableKhachHang.item(row, 0).text()
        ten_kh = self.ui.tableKhachHang.item(row, 1).text()
        email = self.ui.tableKhachHang.item(row, 2).text()

        self.ui.txtMaKH.setText(ma_kh)
        self.ui.txtTenKH.setText(ten_kh)
        self.ui.txtEmail.setText(email)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UserManagement()
    window.show()
    sys.exit(app.exec())