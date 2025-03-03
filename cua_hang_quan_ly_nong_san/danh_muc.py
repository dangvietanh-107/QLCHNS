import sys
import mysql.connector
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog
from PySide6.QtCore import QFile, QIODevice, Qt
from PySide6.QtUiTools import QUiLoader
import openpyxl

# Database Configuration (move this outside the class for global access)
DB_CONFIG = {
    "host": "localhost",  # Replace with your host
    "user": "root",       # Replace with your username
    "password": "",   # Replace with your password
    "database": "quan_ly_nong_san"  # Replace with your database name
}

class DanhMucManagement(QtWidgets.QWidget):  # Changed Class Name
    def __init__(self):
        super().__init__()

        uifile = QFile("danh_muc.ui")  # Changed UI File Name
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

        # Connect UI elements to functions
        self.ui.btnSearch.clicked.connect(self.search_danh_mucs)  # Changed Function Name
        self.ui.btnAdd.clicked.connect(self.add_danh_muc)  # Changed Function Name
        self.ui.btnEdit.clicked.connect(self.edit_danh_muc)  # Changed Function Name
        self.ui.btnDelete.clicked.connect(self.delete_danh_muc)  # Changed Function Name
        self.ui.btnClear.clicked.connect(self.clear_inputs)  # Changed Function Name
        self.ui.btnExport.clicked.connect(self.export_excel)  # Changed Function Name
        self.setup_table()
        self.load_danh_mucs()  # Changed Function Name

        self.ui.tableDanhMuc.itemClicked.connect(self.display_danh_muc_info)  # Changed Table and Function Name

    def connect_db(self):
        """Connect to the MySQL database."""
        return mysql.connector.connect(**DB_CONFIG)

    def setup_table(self):
        """Set up the QTableWidget headers."""
        self.ui.tableDanhMuc.setColumnCount(2)  # Adjust Column Count
        self.ui.tableDanhMuc.setHorizontalHeaderLabels(["Mã Danh Mục", "Tên Danh Mục"])  # Changed Header Labels
        header = self.ui.tableDanhMuc.horizontalHeader()
        for col in range(self.ui.tableDanhMuc.columnCount()):
            header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.ui.tableDanhMuc.setStyleSheet("QTableWidget::item { text-align: center; }")

    def load_danh_mucs(self):  # Changed Function Name
        """Load danh mucs from the database into the table."""  # Changed Docstring
        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql = "SELECT ma_danh_muc, ten_danh_muc FROM danh_muc ORDER BY ma_danh_muc"  # Changed SQL Query, Added ORDER BY
            cursor.execute(sql)
            danh_mucs = cursor.fetchall()  # Changed Variable Name

            self.ui.tableDanhMuc.setRowCount(len(danh_mucs))  # Changed Variable Name
            for row, danh_muc in enumerate(danh_mucs):  # Changed Variable Name
                self.ui.tableDanhMuc.setItem(row, 0, QTableWidgetItem(str(danh_muc[0])))  # Changed Table and data access
                self.ui.tableDanhMuc.setItem(row, 1, QTableWidgetItem(danh_muc[1]))  # Changed Table and data access

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def search_danh_mucs(self):  # Changed Function Name
        """Search for danh mucs based on the search term."""  # Changed Docstring
        keyword = self.ui.txtSearch.text().strip()
        if not keyword:
            self.load_danh_mucs()  # Changed Function Name
            return
        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql = """SELECT ma_danh_muc, ten_danh_muc
                     FROM danh_muc
                     WHERE (ma_danh_muc LIKE %s
                        OR ten_danh_muc LIKE %s)
                     ORDER BY ma_danh_muc"""  # Added ORDER BY
            value = ('%' + keyword + '%',)*2
            cursor.execute(sql, value)
            danh_mucs = cursor.fetchall()  # Changed Variable Name

            if not danh_mucs:  # Changed Variable Name
                QMessageBox.information(self, "Thông báo", "Không tìm thấy danh mục với thông tin này.")
                self.load_danh_mucs()  # Changed Function Name
                return

            self.ui.tableDanhMuc.setRowCount(len(danh_mucs))  # Changed Variable Name
            for row, danh_muc in enumerate(danh_mucs):  # Changed Variable Name
                self.ui.tableDanhMuc.setItem(row, 0, QTableWidgetItem(str(danh_muc[0])))  # Changed Table and data access
                self.ui.tableDanhMuc.setItem(row, 1, QTableWidgetItem(danh_muc[1]))  # Changed Table and data access

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def add_danh_muc(self):  # Changed Function Name
        """Add a new danh muc to the database."""  # Changed Docstring
        ma_danh_muc = self.ui.txtMaDanhMuc.text().strip()
        ten_danh_muc = self.ui.txtTenDanhMuc.text().strip()

        if not ma_danh_muc or not ten_danh_muc:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin.");
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql_check_ma = "SELECT ma_danh_muc FROM danh_muc WHERE ma_danh_muc = %s"  #Check if ma_danh_muc already exists
            cursor.execute(sql_check_ma, (ma_danh_muc,))
            result_ma = cursor.fetchone()
            if result_ma:
                QMessageBox.warning(self, "Lỗi", "Mã danh mục đã tồn tại.");
                return
            
            sql_check_ten = "SELECT ten_danh_muc FROM danh_muc WHERE ten_danh_muc = %s"  #Check if ten_danh_muc already exists
            cursor.execute(sql_check_ten, (ten_danh_muc,))
            result_ten = cursor.fetchone()
            if result_ten:
                QMessageBox.warning(self, "Lỗi", "Tên danh mục đã tồn tại.");
                return

            sql = """INSERT INTO danh_muc (ma_danh_muc, ten_danh_muc)
                     VALUES (%s, %s)"""
            values = (ma_danh_muc, ten_danh_muc)
            cursor.execute(sql, values)
            conn.commit()

            QMessageBox.information(self, "Thành công", "Thêm danh mục thành công!")
            self.load_danh_mucs()  # Changed Function Name
            self.clear_inputs()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def edit_danh_muc(self):  # Changed Function Name
        """Edit an existing danh muc in the database."""  # Changed Docstring
        ma_danh_muc = self.ui.txtMaDanhMuc.text().strip()
        ten_danh_muc = self.ui.txtTenDanhMuc.text().strip()

        if not ma_danh_muc or not ten_danh_muc:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin.");
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            #Check if the new name already exists for a *different* category
            sql_check = "SELECT ten_danh_muc FROM danh_muc WHERE ten_danh_muc = %s AND ma_danh_muc != %s"
            cursor.execute(sql_check, (ten_danh_muc, ma_danh_muc))
            result = cursor.fetchone()
            if result:
                QMessageBox.warning(self, "Lỗi", "Tên danh mục đã tồn tại cho một danh mục khác.");
                return

            sql = """UPDATE danh_muc
                     SET ten_danh_muc = %s
                     WHERE ma_danh_muc = %s"""
            values = (ten_danh_muc, ma_danh_muc)
            cursor.execute(sql, values)
            conn.commit()

            if cursor.rowcount == 0:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy danh mục để sửa.")
                return

            QMessageBox.information(self, "Thành công", "Sửa danh mục thành công!")
            self.load_danh_mucs()  # Changed Function Name
            self.clear_inputs()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def delete_danh_muc(self):  # Changed Function Name
        """Delete a danh muc from the database."""  # Changed Docstring
        ma_danh_muc = self.ui.txtMaDanhMuc.text().strip()
        if not ma_danh_muc:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã danh mục để xóa.")
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql = "DELETE FROM danh_muc WHERE ma_danh_muc = %s"
            cursor.execute(sql, (ma_danh_muc,))
            conn.commit()
            if cursor.rowcount == 0:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy danh mục để xóa.")
                return

            QMessageBox.information(self, "Thành công", "Xóa danh mục thành công!")
            self.load_danh_mucs()  # Changed Function Name
            self.clear_inputs()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def clear_inputs(self):
        """Clear the input fields."""
        self.ui.txtMaDanhMuc.clear()
        self.ui.txtTenDanhMuc.clear()

    def export_excel(self):  # Changed Function Name
        """Export data from the table to an Excel file."""  # Changed Docstring
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Chọn đường dẫn để lưu", "", "Excel Files (*.xlsx)", options=options)

        if filename:
            try:
                conn = self.connect_db()
                cursor = conn.cursor()

                sql = "SELECT ma_danh_muc, ten_danh_muc FROM danh_muc ORDER BY ma_danh_muc" #Added order by here too
                cursor.execute(sql)
                danh_mucs = cursor.fetchall()  # Changed Variable Name

                if not danh_mucs:  # Changed Variable Name
                    QMessageBox.warning(self, "Lỗi", "Không có dữ liệu để xuất.")
                    return

                workbook = openpyxl.Workbook()
                sheet = workbook.active

                headers = ["Mã Danh Mục", "Tên Danh Mục"]  # Changed Headers
                sheet.append(headers)

                for danh_muc in danh_mucs:  # Changed Variable Name
                    sheet.append(danh_muc)

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

    def display_danh_muc_info(self, item):  # Changed Function Name
        """Display danh muc information in the input fields when a row is clicked."""  # Changed Docstring
        row = item.row()

        ma_danh_muc = self.ui.tableDanhMuc.item(row, 0).text()  # Changed Table Name
        ten_danh_muc = self.ui.tableDanhMuc.item(row, 1).text()  # Changed Table Name

        self.ui.txtMaDanhMuc.setText(ma_danh_muc)  # Changed Text Edit
        self.ui.txtTenDanhMuc.setText(ten_danh_muc)  # Changed Text Edit


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DanhMucManagement()  # Changed Class Name
    window.show()
    sys.exit(app.exec())