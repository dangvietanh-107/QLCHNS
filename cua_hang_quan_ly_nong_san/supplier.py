import sys
import mysql.connector
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem
from PySide6.QtCore import QFile, QIODevice, Qt
from PySide6.QtUiTools import QUiLoader

# Database Configuration (Replace with your actual settings)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "quan_ly_nong_san"
}

class SupplierWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uifile = QFile("supplier.ui")  # Load the supplier.ui file
        if not uifile.open(QIODevice.ReadOnly):
            print(f"Cannot open {uifile.fileName()}: {uifile.errorString()}")
            sys.exit(-1)

        loader = QUiLoader()
        self.ui = loader.load(uifile, self)
        uifile.close()

        if self.ui is None:
            print(loader.errorString())
            sys.exit(-1)

        self.setCentralWidget(self.ui.centralwidget)

        # Connect buttons and setup the table
        self.ui.btnSearch.clicked.connect(self.search_suppliers)
        self.ui.btnAdd.clicked.connect(self.add_supplier)
        self.ui.btnEdit.clicked.connect(self.edit_supplier)
        self.ui.btnDelete.clicked.connect(self.delete_supplier)
        self.ui.btnClear.clicked.connect(self.clear_inputs)
        self.ui.btnExport.clicked.connect(self.export_excel) #TODO Implement export function
        self.setup_table()

        # Load initial data
        self.load_suppliers()

        #Connect click row
        self.ui.tableNhaCungCap.itemClicked.connect(self.display_supplier_info)

        self.show()

    def connect_db(self):
        """Connect to the mySQL database"""
        return mysql.connector.connect(**DB_CONFIG)

    def setup_table(self):
        """Setup the QTableWidget headers"""
        self.ui.tableNhaCungCap.setColumnCount(4)
        self.ui.tableNhaCungCap.setHorizontalHeaderLabels(["Mã NCC", "Tên NCC", "Số Điện Thoại", "Địa Chỉ"])
        header = self.ui.tableNhaCungCap.horizontalHeader()
        for col in range(self.ui.tableNhaCungCap.columnCount()):
            header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.ui.tableNhaCungCap.setStyleSheet("QTableWidget::item { text-align: center; }")

    def load_suppliers(self):
        """Load suppliers from the database into the table"""
        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql = "SELECT ma_nha_cung_cap, ten_nha_cung_cap, so_dien_thoai, dia_chi FROM nha_cung_cap"
            cursor.execute(sql)
            suppliers = cursor.fetchall()

            self.ui.tableNhaCungCap.setRowCount(len(suppliers))
            for row, supplier in enumerate(suppliers):
                self.ui.tableNhaCungCap.setItem(row, 0, QTableWidgetItem(str(supplier[0])))  # ma_nha_cung_cap
                self.ui.tableNhaCungCap.setItem(row, 1, QTableWidgetItem(supplier[1]))  # ten_nha_cung_cap
                self.ui.tableNhaCungCap.setItem(row, 2, QTableWidgetItem(supplier[2] or ""))  # so_dien_thoai (handle NULL)
                self.ui.tableNhaCungCap.setItem(row, 3, QTableWidgetItem(supplier[3] or ""))  # dia_chi (handle NULL)

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def search_suppliers(self):
        """Search for suppliers based on the search term"""
        keyword = self.ui.txtSearch.text().strip()

        if not keyword:
            self.load_suppliers()
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql = """SELECT ma_nha_cung_cap, ten_nha_cung_cap, so_dien_thoai, dia_chi
                     FROM nha_cung_cap
                     WHERE (ma_nha_cung_cap LIKE %s
                        OR ten_nha_cung_cap LIKE %s
                        OR so_dien_thoai LIKE %s
                        OR dia_chi LIKE %s)"""

            # Create tuple with value for SQL.

            value = ('%' + keyword + '%',)*4

            cursor.execute(sql, value)
            suppliers = cursor.fetchall()
            if not suppliers:
                 QMessageBox.information(self, "Thông báo", "Không tìm thấy nhà cung cấp với thông tin này.")
                 self.load_suppliers()
                 return
            self.ui.tableNhaCungCap.setRowCount(len(suppliers))
            for row, supplier in enumerate(suppliers):
                self.ui.tableNhaCungCap.setItem(row, 0, QTableWidgetItem(str(supplier[0])))  # ma_nha_cung_cap
                self.ui.tableNhaCungCap.setItem(row, 1, QTableWidgetItem(supplier[1]))  # ten_nha_cung_cap
                self.ui.tableNhaCungCap.setItem(row, 2, QTableWidgetItem(supplier[2] or ""))  # so_dien_thoai (handle NULL)
                self.ui.tableNhaCungCap.setItem(row, 3, QTableWidgetItem(supplier[3] or ""))  # dia_chi (handle NULL)

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def add_supplier(self):
        """Add a new supplier to the database"""
        ma_nha_cung_cap = self.ui.txtMaNCC.text().strip()
        ten_nha_cung_cap = self.ui.txtTenNCC.text().strip()
        so_dien_thoai = self.ui.txtSoDienThoai.text().strip()
        dia_chi = self.ui.txtDiaChi.text().strip()

        # Validate input
        if not (ma_nha_cung_cap and ten_nha_cung_cap and so_dien_thoai and dia_chi):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            # Check for duplicate ma_nha_cung_cap
            sql_check = "SELECT ma_nha_cung_cap FROM nha_cung_cap WHERE ma_nha_cung_cap = %s"
            cursor.execute(sql_check, (ma_nha_cung_cap,))
            result = cursor.fetchone()
            if result:
                QMessageBox.warning(self, "Lỗi", "Mã nhà cung cấp đã tồn tại.")
                return

            sql = """INSERT INTO nha_cung_cap (ma_nha_cung_cap, ten_nha_cung_cap, so_dien_thoai, dia_chi)
                     VALUES (%s, %s, %s, %s)"""
            values = (ma_nha_cung_cap, ten_nha_cung_cap, so_dien_thoai, dia_chi)
            cursor.execute(sql, values)
            conn.commit()

            QMessageBox.information(self, "Thành công", "Thêm nhà cung cấp thành công!")
            self.load_suppliers()
            self.clear_inputs()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def edit_supplier(self):
        """Edit an existing supplier in the database"""
        ma_nha_cung_cap = self.ui.txtMaNCC.text().strip()
        ten_nha_cung_cap = self.ui.txtTenNCC.text().strip()
        so_dien_thoai = self.ui.txtSoDienThoai.text().strip()
        dia_chi = self.ui.txtDiaChi.text().strip()

        if not ma_nha_cung_cap:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã nhà cung cấp để sửa.")
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql = """UPDATE nha_cung_cap
                     SET ten_nha_cung_cap = %s, so_dien_thoai = %s, dia_chi = %s
                     WHERE ma_nha_cung_cap = %s"""
            values = (ten_nha_cung_cap, so_dien_thoai, dia_chi, ma_nha_cung_cap)
            cursor.execute(sql, values)
            conn.commit()

            if cursor.rowcount == 0:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy nhà cung cấp để sửa.");
                return

            QMessageBox.information(self, "Thành công", "Sửa nhà cung cấp thành công!")
            self.load_suppliers()
            self.clear_inputs()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def delete_supplier(self):
        """Delete a supplier from the database"""
        ma_nha_cung_cap = self.ui.txtMaNCC.text().strip()
        if not ma_nha_cung_cap:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã nhà cung cấp để xóa.")
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql = "DELETE FROM nha_cung_cap WHERE ma_nha_cung_cap = %s"
            cursor.execute(sql, (ma_nha_cung_cap,))
            conn.commit()
            if cursor.rowcount == 0:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy nhà cung cấp để xóa.");
                return

            QMessageBox.information(self, "Thành công", "Xóa nhà cung cấp thành công!")
            self.load_suppliers()
            self.clear_inputs()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def clear_inputs(self):
        """Clear the input fields"""
        self.ui.txtMaNCC.clear()
        self.ui.txtTenNCC.clear()
        self.ui.txtSoDienThoai.clear()
        self.ui.txtDiaChi.clear()

    def export_excel(self):
        """Placeholder for exporting to Excel"""
        QMessageBox.information(self, "Thông báo", "Chức năng xuất Excel chưa được triển khai.")

    def display_supplier_info(self, item):
        """Display supplier information in the input fields when a row is clicked"""
        row = item.row() #Gets the row number clicked

        ma_nha_cung_cap = self.ui.tableNhaCungCap.item(row, 0).text()
        ten_nha_cung_cap = self.ui.tableNhaCungCap.item(row, 1).text()
        so_dien_thoai = self.ui.tableNhaCungCap.item(row, 2).text()
        dia_chi = self.ui.tableNhaCungCap.item(row, 3).text()

        self.ui.txtMaNCC.setText(ma_nha_cung_cap)
        self.ui.txtTenNCC.setText(ten_nha_cung_cap)
        self.ui.txtSoDienThoai.setText(so_dien_thoai)
        self.ui.txtDiaChi.setText(dia_chi)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SupplierWindow()
    sys.exit(app.exec())