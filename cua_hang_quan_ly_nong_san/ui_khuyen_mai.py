import sys
import mysql.connector
import pandas as pd
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog
from PySide6.QtGui import QIntValidator, QValidator, QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression, QDate, QFile, QIODevice
from decimal import Decimal
from PySide6.QtUiTools import QUiLoader
import datetime

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "quan_ly_nong_san"
}


class KhuyenMaiManagement(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI from the .ui file
        uifile = QFile("khuyen_mai.ui")
        if not uifile.open(QIODevice.ReadOnly):
            print(f"Cannot open {uifile.fileName()}: {uifile.errorString()}")
            sys.exit(-1)
        loader = QUiLoader()
        self.ui = loader.load(uifile, self)
        uifile.close()
        if self.ui is None:
            print(loader.errorString())
            sys.exit(-1)

        self.setCentralWidget(self.ui.centralwidget)  # Use centralwidget from .ui

        # Connect Buttons
        self.ui.btnAdd.clicked.connect(self.add_khuyen_mai)
        self.ui.btnEdit.clicked.connect(self.edit_khuyen_mai)
        self.ui.btnDelete.clicked.connect(self.delete_khuyen_mai)
        self.ui.btnExport.clicked.connect(self.export_to_excel)
        self.ui.btnSearch.clicked.connect(self.search_khuyen_mai)
        self.ui.btnClear.clicked.connect(self.clear_input_fields)

        # Configure Table
        self.setup_table()

        # Load Data
        self.load_khuyen_mai()

        # Validators
        regex = QRegularExpression("^[0-9]{1,3}$")
        validator = QRegularExpressionValidator(regex)
        self.ui.txtPhanTramGiam.setValidator(validator)

        # Connect table cell click to display details
        self.ui.tableKhuyenMai.cellClicked.connect(self.display_khuyen_mai_details)

        self.ui.statusbar = self.ui.statusbar # Access the statusbar

        self.show() # Make sure the window is visible

    def clear_input_fields(self):
        """Clear all the text input"""
        self.ui.txtMaKM.clear()
        self.ui.txtTenKM.clear()
        self.ui.txtPhanTramGiam.clear()
        self.ui.dateNgayBatDau.setDate(QDate.currentDate())
        self.ui.dateNgayKetThuc.setDate(QDate.currentDate())
        self.ui.txtDonToiThieu.clear()

    def connect_db(self):
        return mysql.connector.connect(**DB_CONFIG)

    def setup_table(self):
        """Setup QTableWidget for khuyen_mai data"""
        self.ui.tableKhuyenMai.setColumnCount(7) # Add 1 column
        self.ui.tableKhuyenMai.setHorizontalHeaderLabels(["Mã KM", "Tên KM", "Phần Trăm Giảm", "Ngày Bắt Đầu", "Ngày Kết Thúc", "Đơn Tối Thiểu", "Trạng Thái"]) #Add column
        header = self.ui.tableKhuyenMai.horizontalHeader()
        for col in range(self.ui.tableKhuyenMai.columnCount()):
            header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)

    def update_table_row(self, row_idx, row_data):
        """Helper function to update a row in the table"""
        today = datetime.date.today()
        start_date = datetime.datetime.strptime(row_data[3], '%Y-%m-%d').date() if isinstance(row_data[3], str) else row_data[3]
        end_date = datetime.datetime.strptime(row_data[4], '%Y-%m-%d').date() if isinstance(row_data[4], str) else row_data[4]
        status = "Hết hạn" if today > end_date else "Còn hạn" #Setting status base on the date

        table_data = list(row_data) # Convert tuple to list so that i can append status
        table_data.append(status)

        for col_idx, data in enumerate(table_data):
            item = QTableWidgetItem(str(data))
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.ui.tableKhuyenMai.setItem(row_idx, col_idx, item)

    def load_khuyen_mai(self, search_query=None):
        """Load and display KhuyenMai data from the database"""
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            if search_query:
                sql = """SELECT ma_km, ten_ma_km, phan_tram_giam, ngay_bat_dau_km, ngay_ket_thuc_km, don_toi_thieu
                        FROM khuyen_mai WHERE ma_km LIKE %s OR ten_ma_km LIKE %s"""
                cursor.execute(sql, (f"%{search_query}%", f"%{search_query}%"))
            else:
                sql = "SELECT ma_km, ten_ma_km, phan_tram_giam, ngay_bat_dau_km, ngay_ket_thuc_km, don_toi_thieu FROM khuyen_mai"
                cursor.execute(sql)

            rows = cursor.fetchall()
            self.ui.tableKhuyenMai.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                self.update_table_row(row_idx, row_data)

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error loading data: {err}")
            self.ui.statusbar.showMessage(f"Database Error: {err}", 5000) # Display in statusbar
        finally:
            cursor.close()
            conn.close()

    def display_khuyen_mai_details(self, row, column):
        """Hiển thị chi tiết khuyến mãi khi một ô được click."""
        # Lấy dữ liệu từ hàng được chọn
        try: #Added exception handling for missing Item.
            ma_km = self.ui.tableKhuyenMai.item(row, 0).text()
            ten_ma_km = self.ui.tableKhuyenMai.item(row, 1).text()
            phan_tram_giam = self.ui.tableKhuyenMai.item(row, 2).text()
            ngay_bat_dau_km = self.ui.tableKhuyenMai.item(row, 3).text()
            ngay_ket_thuc_km = self.ui.tableKhuyenMai.item(row, 4).text()
            don_toi_thieu = self.ui.tableKhuyenMai.item(row, 5).text()
            status = self.ui.tableKhuyenMai.item(row, 6).text()

        except AttributeError as e:
            print(f"AttributeError: {e}.  This likely means the cell is empty.")
            return # Exit if the cell is empty.


        # Hiển thị dữ liệu lên các widget tương ứng
        self.ui.txtMaKM.setText(ma_km)
        self.ui.txtTenKM.setText(ten_ma_km)
        self.ui.txtPhanTramGiam.setText(phan_tram_giam)
        self.ui.dateNgayBatDau.setDate(QDate.fromString(ngay_bat_dau_km, "yyyy-MM-dd"))
        self.ui.dateNgayKetThuc.setDate(QDate.fromString(ngay_ket_thuc_km, "yyyy-MM-dd"))
        self.ui.txtDonToiThieu.setText(don_toi_thieu)

        #Showed the notification that the KM already expired if status == Het han
        if status == "Hết hạn":
            QMessageBox.warning(self, "Lưu ý", f"Khuyến mãi {ma_km} đã hết hạn và không thể sử dụng.")

    def add_khuyen_mai(self):
        """Add a new KhuyenMai record to the database"""
        try:
            ma_km = self.ui.txtMaKM.text().strip()
            ten_ma_km = self.ui.txtTenKM.text().strip()
            phan_tram_giam = self.ui.txtPhanTramGiam.text().strip()
            ngay_bat_dau_km = self.ui.dateNgayBatDau.date().toString(QtCore.Qt.DateFormat.ISODate)
            ngay_ket_thuc_km = self.ui.dateNgayKetThuc.date().toString(QtCore.Qt.DateFormat.ISODate)
            don_toi_thieu = self.ui.txtDonToiThieu.text().strip()

            # Validate inputs (add more validation as needed)
            if not all([ma_km, ten_ma_km, phan_tram_giam, ngay_bat_dau_km, ngay_ket_thuc_km, don_toi_thieu]):
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return

            # Check if ma_km already exists
            if self.khuyen_mai_exists(ma_km):
                QMessageBox.warning(self, "Lỗi", f"Mã khuyến mãi '{ma_km}' đã tồn tại!")
                return

            #Validate Date
            start_date = datetime.datetime.strptime(ngay_bat_dau_km, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(ngay_ket_thuc_km, '%Y-%m-%d').date()
            if start_date > end_date: #If start_date is bigger than end_date, it is invalid.
                QMessageBox.warning(self, "Lỗi", f"Ngày bắt đầu không thể lớn hơn ngày kết thúc")
                return

            conn = self.connect_db()
            cursor = conn.cursor()
            sql = """INSERT INTO khuyen_mai (ma_km, ten_ma_km, phan_tram_giam, ngay_bat_dau_km, ngay_ket_thuc_km, don_toi_thieu)
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            val = (ma_km, ten_ma_km, phan_tram_giam, ngay_bat_dau_km, ngay_ket_thuc_km, don_toi_thieu)
            cursor.execute(sql, val)
            conn.commit()
            QMessageBox.information(self, "Thành công", "Thêm khuyến mãi thành công!")
            self.load_khuyen_mai()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
            self.ui.statusbar.showMessage(f"MySQL Error: {err}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi : {e}") #catch exception
            self.ui.statusbar.showMessage(f"Exception: {e}", 5000) #display it
        finally:
            cursor.close()
            conn.close()

    def edit_khuyen_mai(self):
        """Edit an existing KhuyenMai record"""
        try:
            ma_km = self.ui.txtMaKM.text().strip()
            ten_ma_km = self.ui.txtTenKM.text().strip()
            phan_tram_giam = self.ui.txtPhanTramGiam.text().strip()
            ngay_bat_dau_km = self.ui.dateNgayBatDau.date().toString(QtCore.Qt.DateFormat.ISODate)
            ngay_ket_thuc_km = self.ui.dateNgayKetThuc.date().toString(QtCore.Qt.DateFormat.ISODate)
            don_toi_thieu = self.ui.txtDonToiThieu.text().strip()

            # Validate inputs (add more validation as needed)
            if not all([ma_km, ten_ma_km, phan_tram_giam, ngay_bat_dau_km, ngay_ket_thuc_km, don_toi_thieu]):
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return

            # Check if ma_km exists
            if not self.khuyen_mai_exists(ma_km):
                QMessageBox.warning(self, "Lỗi", f"Mã khuyến mãi '{ma_km}' không tồn tại!")
                return

            #Validate Date
            start_date = datetime.datetime.strptime(ngay_bat_dau_km, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(ngay_ket_thuc_km, '%Y-%m-%d').date()
            if start_date > end_date: #If start_date is bigger than end_date, it is invalid.
                QMessageBox.warning(self, "Lỗi", f"Ngày bắt đầu không thể lớn hơn ngày kết thúc")
                return

            conn = self.connect_db()
            cursor = conn.cursor()

            sql = """UPDATE khuyen_mai SET ten_ma_km=%s, phan_tram_giam=%s, ngay_bat_dau_km=%s, ngay_ket_thuc_km=%s, don_toi_thieu=%s
                     WHERE ma_km=%s"""
            val = (ten_ma_km, phan_tram_giam, ngay_bat_dau_km, ngay_ket_thuc_km, don_toi_thieu, ma_km)
            cursor.execute(sql, val)
            conn.commit()
            QMessageBox.information(self, "Thành công", "Cập nhật khuyến mãi thành công!")
            self.load_khuyen_mai()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
            self.ui.statusbar.showMessage(f"MySQL Error: {err}", 5000)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi : {e}") #catch exception
            self.ui.statusbar.showMessage(f"Exception: {e}", 5000) #display it

        finally:
            cursor.close()
            conn.close()

    def delete_khuyen_mai(self):
        """Delete a KhuyenMai record"""
        ma_km = self.ui.txtMaKM.text().strip()

        # Check if ma_km exists
        if not self.khuyen_mai_exists(ma_km):
            QMessageBox.warning(self, "Lỗi", f"Mã khuyến mãi '{ma_km}' không tồn tại!")
            return

        reply = QMessageBox.question(self, 'Xóa Khuyến Mãi', f"Bạn có chắc chắn muốn xóa khuyến mãi {ma_km}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn = self.connect_db()
            cursor = conn.cursor()

            sql = "DELETE FROM khuyen_mai WHERE ma_km=%s"
            cursor.execute(sql, (ma_km,))
            conn.commit()
            QMessageBox.information(self, "Thành công", "Xóa khuyến mãi thành công!")
            self.load_khuyen_mai()
            cursor.close()
            conn.close()

    def search_khuyen_mai(self):
        """Search for KhuyenMai records"""
        keyword = self.ui.txtSearch.text().strip()
        self.load_khuyen_mai(search_query=keyword)

    def export_to_excel(self):
        """Export KhuyenMai data to an Excel file"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file", "", "Excel Files (*.xlsx)")

        if not file_path:
            return

        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            sql = "SELECT ma_km, ten_ma_km, phan_tram_giam, ngay_bat_dau_km, ngay_ket_thuc_km, don_toi_thieu FROM khuyen_mai"
            cursor.execute(sql)
            rows = cursor.fetchall()

            df = pd.DataFrame(rows, columns=["Mã KM", "Tên KM", "Phần Trăm Giảm", "Ngày Bắt Đầu", "Ngày Kết Thúc", "Đơn Tối Thiểu"])
            df.to_excel(file_path, index=False, engine='openpyxl')

            QMessageBox.information(self, "Thành công", f"Dữ liệu đã được xuất ra file {file_path}")

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi : {e}")

        finally:
            cursor.close()
            conn.close()

    def khuyen_mai_exists(self, ma_km):
        """Check if a KhuyenMai record exists with the given ma_km"""
        conn = self.connect_db()
        cursor = conn.cursor()
        sql = "SELECT ma_km FROM khuyen_mai WHERE ma_km=%s"
        cursor.execute(sql, (ma_km,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = KhuyenMaiManagement()
    sys.exit(app.exec())