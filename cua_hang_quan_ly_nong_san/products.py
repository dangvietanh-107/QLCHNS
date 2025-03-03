import sys
import mysql.connector
import re
from matplotlib.widgets import Cursor
from numpy import conj
import pandas as pd
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog, QLabel
from PySide6.QtGui import QPixmap, QImage, QDoubleValidator, QIntValidator
from PySide6.QtCore import Qt, QFile, QIODevice
from io import BytesIO
from decimal import Decimal
from PySide6.QtUiTools import QUiLoader

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "quan_ly_nong_san"
}

class ManageData(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uifile = QFile("products.ui")
        if not uifile.open(QIODevice.ReadOnly):
            print(f"Cannot open {uifile.fileName()}: {uifile.errorString()}")
            sys.exit(-1)

        loader = QUiLoader()
        self.ui = loader.load(uifile, self)

        uifile.close()
        if self.ui is None:
            print(loader.errorString())
            sys.exit(-1)

        self.setCentralWidget(self.ui.centralwidget) #Correct central Widget

        # Connect Buttons to Functions
        self.ui.btnAdd.clicked.connect(self.add_product)
        self.ui.btnEdit.clicked.connect(self.edit_product)
        self.ui.btnDelete.clicked.connect(self.delete_product)
        self.ui.btnExport.clicked.connect(self.export_to_excel)
        self.ui.btnSearch.clicked.connect(self.search_product)
        self.ui.btnClear.clicked.connect(self.clear_textboxes)
        self.ui.btnChonAnh.clicked.connect(self.browse_image)  # Corrected button name

        # Configure Table
        self.setup_table()

        # Load Data from Database
        self.load_products()
        self.load_categories()
        self.load_suppliers()

        # Set default for DoublespinBox
        self.ui.doubleGia.setDecimals(2) # Decimal Numbers
        self.ui.doubleGia.setMaximum(9999999.99) # Maxium values for the double spinbox
        self.ui.doubleSoLuongTon.setMaximum(9999999.99) # Maxium values for the double spinbox

        # Validators
        self.int_validator = QIntValidator()

        #Set Input Validator to Integer Only:
        self.ui.txtMaSP.setValidator(self.int_validator)
        self.update_inventory_type_options()  # Initial setup for unit selection

        # Connect cmbCategory currentIndexChanged signal to the update_inventory_type_options method
        self.ui.cmbCategory.currentIndexChanged.connect(self.update_inventory_type_options)

        self.show()

    def clear_textboxes(self):
        """Clear all the text input"""
        self.ui.txtMaSP.clear()
        self.ui.txtTenSP.clear()
        self.ui.doubleGia.setValue(0.0) #Sets back to 0.0 value
        self.ui.doubleSoLuongTon.setValue(0.0) #Sets back to 0.0 value
        self.ui.cmbCategory.setCurrentIndex(-1) # clear the combo box
        self.ui.cmbSupplier.setCurrentIndex(-1)  # Clear Supplier Combo Box Too
        self.ui.txtAnh.clear()
        self.ui.cbbDonVi.setCurrentIndex(-1) # Reset the combo box when clear and the selection is set to none.

    def connect_db(self):
        """Connect to the mySQL database"""
        return mysql.connector.connect(**DB_CONFIG)

    def setup_table(self):
        """Setup QTableWidget with images and product information"""
        self.ui.tableSanPham.setColumnCount(7) # One Less Column
        self.ui.tableSanPham.setHorizontalHeaderLabels(["Mã SP", "Tên SP", "Danh mục", "Giá","Số lượng tồn", "Nhà cung cấp", "Ảnh"])  # Modified header
        # make it resize for the columns
        self.ui.tableSanPham.setColumnWidth(6, 120)
        header = self.ui.tableSanPham.horizontalHeader()
        for col in range(self.ui.tableSanPham.columnCount() - 1):
            header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)

        # Align center and set height
        self.ui.tableSanPham.setStyleSheet("QTableWidget::item { text-align: center; }")
        self.ui.tableSanPham.verticalHeader().setDefaultSectionSize(80)

        # Add action and load the functions
        self.ui.tableSanPham.selectionModel().selectionChanged.connect(self.on_table_item_selected)

    def update_input_validator(self):
        """Cập nhật validator cho trường nhập giá trị tồn kho - Not used since we're using DoubleSpinBox"""
        pass

    def update_inventory_type_options(self):
        """
        Cập nhật các lựa chọn trong cbbDonVi dựa trên danh mục được chọn
        """
        self.ui.cbbDonVi.clear()
        category_name = self.ui.cmbCategory.currentText().lower() #Get the text selected and lowercase it

        if "thịt" in category_name or "hải sản" in category_name:
            self.ui.cbbDonVi.addItem("con")
            self.ui.cbbDonVi.addItem("kg")
        elif "rau" in category_name or "củ" in category_name:
            self.ui.cbbDonVi.addItem("kg") #Only has KG option
        elif "trái cây" in category_name or "hoa quả" in category_name:
            self.ui.cbbDonVi.addItem("quả")
            self.ui.cbbDonVi.addItem("kg")
        self.ui.cbbDonVi.setCurrentIndex(-1) # To set it for no selection

    def on_table_item_selected(self, selected, deselected):
        """When a row is selected, add the selected to the text boxes"""
        selected_row = self.ui.tableSanPham.currentRow()
        if selected_row == -1:
            return

        # *** CORRECTED: Get the product ID from the selected row in the table ***
        product_id_item = self.ui.tableSanPham.item(selected_row, 0) # Column 0 is ma_san_pham
        if product_id_item is None:
            QMessageBox.warning(self, "Lỗi", "Không thể lấy ID sản phẩm từ bảng!")
            return  # Exit if no ID found
        product_id = product_id_item.text()
        # *********************************************************************

        conn = self.connect_db()
        cursor = conn.cursor()
        try:

            if self.is_product_in_database(product_id): #check if item in database
                cursor.execute("""
                    SELECT sp.ma_san_pham, sp.ten_san_pham, dm.ten_danh_muc, sp.gia, sp.so_luong_ton, ncc.ten_nha_cung_cap, sp.anh
                    FROM san_pham sp
                    JOIN danh_muc dm ON sp.ma_danh_muc = dm.ma_danh_muc
                    LEFT JOIN nha_cung_cap ncc ON sp.ma_nha_cung_cap = ncc.ma_nha_cung_cap
                    WHERE sp.ma_san_pham = %s
                """, (product_id,)) #Load again base on the Product ID to refresh
                product = cursor.fetchone()

                #Clear Combo Boxes before set again
                self.ui.cmbCategory.clear()
                self.load_categories() #Reload

                self.ui.cmbSupplier.clear()
                self.load_suppliers() #Reload

                if product:
                    ma_san_pham, ten_san_pham, ten_danh_muc, gia, so_luong_ton, ten_nha_cung_cap, anh = product

                    self.ui.txtMaSP.setText(str(ma_san_pham))
                    self.ui.txtTenSP.setText(str(ten_san_pham))
                    self.ui.doubleGia.setValue(gia) #Load and set text
                    self.ui.doubleSoLuongTon.setValue(so_luong_ton) #Load and set text

                    #Select Category By Name from cmbCategory
                    for i in range(self.ui.cmbCategory.count()):
                        if self.ui.cmbCategory.itemText(i) == ten_danh_muc:
                            self.ui.cmbCategory.setCurrentIndex(i)
                            break

                    #Select Supplier By Name from cmbSupplier
                    for i in range(self.ui.cmbSupplier.count()):
                        if self.ui.cmbSupplier.itemText(i) == ten_nha_cung_cap:
                            self.ui.cmbSupplier.setCurrentIndex(i)
                            break

                    # Set cbbDonVi for the selected
                    for i in range(self.ui.cbbDonVi.count()):
                        # Get 'don_vi' from database again.
                        cursor.execute("SELECT don_vi FROM san_pham WHERE ma_san_pham=%s", (product_id,))
                        don_vi = cursor.fetchone()[0] #Get the first
                        if self.ui.cbbDonVi.itemText(i) == don_vi: #If the item is equal to database
                            self.ui.cbbDonVi.setCurrentIndex(i) # Select.

            else:
                QMessageBox.warning(self, "Lỗi", "ID sản phẩm không tồn tại trong database!") #Error if ID not in dataBase.
                self.load_products()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def load_products(self):
        """Displays all products in the database"""
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT sp.ma_san_pham, sp.ten_san_pham, dm.ten_danh_muc, sp.gia, sp.so_luong_ton, ncc.ten_nha_cung_cap, sp.anh
                FROM san_pham sp
                JOIN danh_muc dm ON sp.ma_danh_muc = dm.ma_danh_muc
                LEFT JOIN nha_cung_cap ncc ON sp.ma_nha_cung_cap = ncc.ma_nha_cung_cap
            """)
            rows = cursor.fetchall()

            self.ui.tableSanPham.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                # Common properties
                ma_san_pham, ten_san_pham, ten_danh_muc, gia, so_luong_ton, ten_nha_cung_cap, anh = row_data

                self.ui.tableSanPham.setItem(row_idx, 0, QTableWidgetItem(str(ma_san_pham)))
                self.ui.tableSanPham.setItem(row_idx, 1, QTableWidgetItem(str(ten_san_pham)))
                self.ui.tableSanPham.setItem(row_idx, 2, QTableWidgetItem(str(ten_danh_muc)))
                self.ui.tableSanPham.setItem(row_idx, 3, QTableWidgetItem(str(gia)))
                self.ui.tableSanPham.setItem(row_idx, 4, QTableWidgetItem(str(so_luong_ton)))
                self.ui.tableSanPham.setItem(row_idx, 5, QTableWidgetItem(str(ten_nha_cung_cap or "")))

                # Xử lý cột ảnh
                image_path = anh
                if image_path:
                    try:
                        pixmap = QPixmap(image_path)
                        pixmap = pixmap.scaled(100, 75, Qt.AspectRatioMode.KeepAspectRatio)  # Correct class call
                        image_label = QLabel()
                        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  #Correct class call
                        image_label.setPixmap(pixmap)
                        self.ui.tableSanPham.setCellWidget(row_idx, 6, image_label)

                    except Exception as e:
                        print(f"Lỗi hiển thị ảnh: {e}")
                        # Hiển thị ảnh lỗi hoặc ảnh mặc định nếu có lỗi
                        default_pixmap = QPixmap("images/default_product.png")
                        default_pixmap = default_pixmap.scaled(100, 75, Qt.AspectRatioMode.KeepAspectRatio)  # Correct class call
                        image_label = QLabel()
                        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  #Correct class call
                        image_label.setPixmap(default_pixmap)
                        self.ui.tableSanPham.setCellWidget(row_idx, 6, image_label)
                else:
                    # Hiển thị ảnh mặc định nếu không có đường dẫn ảnh
                    default_pixmap = QPixmap("images/default_product.png")
                    default_pixmap = default_pixmap.scaled(100, 75, Qt.AspectRatioMode.KeepAspectRatio)  # Correct class call
                    image_label = QLabel()
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter) #Correct class call
                    image_label.setPixmap(default_pixmap)
                    self.ui.tableSanPham.setCellWidget(row_idx, 6, image_label)

        except Exception as e:
            print(f"Error in load_products: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def load_categories(self):
        """Nạp danh mục sản phẩm vào QComboBox"""
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT ma_danh_muc, ten_danh_muc FROM danh_muc")
            categories = cursor.fetchall()
            self.ui.cmbCategory.clear()

            for category in categories:
                self.ui.cmbCategory.addItem(category[1], category[0]) # the itemData will be used to keep track

            self.ui.cmbCategory.setCurrentIndex(-1) # set to no selection by default

        except Exception as e:
            print(f"Error in load_categories: {e}")
        finally:
           if cursor:
                cursor.close()
           if conn:
               conn.close()

    def load_suppliers(self):
        """Nạp danh sách nhà cung cấp vào QComboBox"""
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT ma_nha_cung_cap, ten_nha_cung_cap FROM nha_cung_cap")
            suppliers = cursor.fetchall()
            self.ui.cmbSupplier.clear()  # Clear existing items before loading

            for supplier in suppliers:
                self.ui.cmbSupplier.addItem(supplier[1], supplier[0])  # Add supplier name and ID

            self.ui.cmbSupplier.setCurrentIndex(-1)  # Set to no selection

        except Exception as e:
            print(f"Error in load_suppliers: {e}")
        finally:
           if cursor:
               cursor.close()
           if conn:
               conn.close()

    def browse_image(self):
        """Mở hộp thoại chọn file ảnh và hiển thị đường dẫn"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh sản phẩm", "", "Ảnh (*.png *.jpg *.jpeg)")
        if file_path:
            self.ui.txtAnh.setText(file_path)

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def is_positive(self, value):
        try:
            return float(value) > 0
        except ValueError:
            return False

    def add_product(self):
        """Thêm sản phẩm mới, không cho phép trùng ID, bao gồm cả ảnh"""
        product_id = self.ui.txtMaSP.text()
        name = self.ui.txtTenSP.text()

        if self.ui.cmbCategory.currentIndex() == -1:  # Check if any item selected from combobox
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn danh mục sản phẩm!")
            return
        category_id = self.ui.cmbCategory.itemData(self.ui.cmbCategory.currentIndex()) # This line needs to take the Int Value

        if self.ui.cmbSupplier.currentIndex() == -1:  # Check if any supplier is selected
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhà cung cấp!")
            return
        supplier_id = self.ui.cmbSupplier.itemData(self.ui.cmbSupplier.currentIndex())

        price = self.ui.doubleGia.value()  # Get the float value directly

        if self.ui.cbbDonVi.currentIndex() == -1:  # Check if any unit is selected
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn đơn vị sản phẩm!")
            return
        inventory_type = self.ui.cbbDonVi.currentText()

        inventory_value = self.ui.doubleSoLuongTon.value() #Get the float value directly
        image_path = self.ui.txtAnh.text()

        if not product_id or not name or not price or inventory_type is None or not inventory_value:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin cơ bản!")
            return

        if not self.is_positive(price):
            QMessageBox.warning(self, "Lỗi", "Giá phải là một số dương!");
            return

        # Check inventory_value based on inventory_type
        if inventory_type in ("quả", "con"):
            if float(inventory_value) != int(inventory_value) or float(inventory_value) <=0:
                QMessageBox.warning(self, "Lỗi", "Số lượng (Quả/Con) phải là số nguyên dương!");
                return
            inventory_value = int(inventory_value)

        else:  # "kg"
            if not self.is_positive(inventory_value):
                QMessageBox.warning(self, "Lỗi", "Số lượng (Kg) phải là số dương!");
                return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            # Check if product ID already exists
            cursor.execute("SELECT * FROM san_pham WHERE ma_san_pham = %s", (product_id,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Lỗi", "ID sản phẩm đã tồn tại! Vui lòng nhập ID khác.")
                return

            # Confirm add product
            confirm = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn thêm sản phẩm này?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.No:
                return

            sql = """INSERT INTO san_pham (ma_san_pham, ten_san_pham, ma_danh_muc, gia, so_luong_ton, ma_nha_cung_cap, anh, don_vi)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (product_id, name, category_id, price, inventory_value, supplier_id, image_path, inventory_type)
            cursor.execute(sql, values)
            conn.commit()
            QMessageBox.information(self, "Thành công", "Thêm sản phẩm thành công!")
            self.load_products()
            self.load_categories()  # Refresh the combo boxes after adding
            self.load_suppliers()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")

        finally:
            cursor.close()
            conn.close()


    def edit_product(self):
        """Edit the values"""
        product_id = self.ui.txtMaSP.text()
        name = self.ui.txtTenSP.text()

        if self.ui.cmbCategory.currentIndex() == -1:  # Check if any item selected from combobox
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn danh mục sản phẩm!")
            return
        category_id = self.ui.cmbCategory.itemData(self.ui.cmbCategory.currentIndex()) # This line needs to take the Int Value

        if self.ui.cmbSupplier.currentIndex() == -1:  # Check if any supplier is selected
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhà cung cấp!")
            return
        supplier_id = self.ui.cmbSupplier.itemData(self.ui.cmbSupplier.currentIndex())

        price = self.ui.doubleGia.value()  # Get the float value directly
        inventory_type = self.ui.cbbDonVi.currentText()
        inventory_value = self.ui.doubleSoLuongTon.value() #Get the float value directly
        image_path = self.ui.txtAnh.text()

        #Validate all information
        if not product_id or not name or not price or inventory_type is None or not inventory_value:
           QMessageBox.warning(self, "Lỗi", "Please fill all field");
           return

        if not self.is_positive(price):
            QMessageBox.warning(self, "Lỗi", "Giá phải là một số dương!");
            return

        if not self.is_positive(inventory_value):
            QMessageBox.warning(self, "Lỗi", "Số lượng tồn phải là một số dương!");
            return

        conn = self.connect_db()
        Cursor = conn.cursor()
        conj = conn

        try:

            sql = """UPDATE san_pham
                    SET ten_san_pham=%s, ma_danh_muc=%s, gia=%s, so_luong_ton=%s, ma_nha_cung_cap=%s , anh=%s, don_vi=%s
                    WHERE ma_san_pham=%s"""
            values = (name, category_id, price, inventory_value, supplier_id, image_path, inventory_type, product_id)  # last argument must be product_id
            # Execute the query
            Cursor.execute(sql, values)
            conj.commit()
            QMessageBox.information(self, "Thành công", "Cập nhật sản phẩm thành công!")
            self.load_products()  # Refresh
            self.load_categories()  # Refresh the combo boxes after edit
            self.load_suppliers()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {err}")

        finally:
            # Clean up
            Cursor.close()
            conj.close()

    def delete_product(self):
        """Xóa sản phẩm"""
        product_id = self.ui.txtMaSP.text()

        if not product_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập ID sản phẩm cần xóa!")
            return

        # Confirm delete product
        confirm = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa sản phẩm này?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.No:
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            # Check if ID exists
            cursor.execute("SELECT * FROM san_pham WHERE ma_san_pham = %s", (product_id,))
            if not cursor.fetchone():
                QMessageBox.warning(self, "Lỗi", "ID sản phẩm không tồn tại!")
                return

            cursor.execute("DELETE FROM san_pham WHERE ma_san_pham=%s", (product_id,))
            conn.commit()
            QMessageBox.information(self, "Thành công", "Xóa sản phẩm thành công!")
            self.load_products()
            self.load_categories()  # Refresh the combo boxes after delete
            self.load_suppliers()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {err}")
        finally:
            cursor.close()
            conn.close()

    def search_product(self):
        """Tìm kiếm sản phẩm"""
        keyword = self.ui.txtSearch.text().strip()

        conn = self.connect_db()
        cursor = conn.cursor()

        sql = """SELECT sp.ma_san_pham, sp.ten_san_pham, dm.ten_danh_muc, sp.gia, sp.so_luong_ton, ncc.ten_nha_cung_cap, sp.anh
                 FROM san_pham sp
                 JOIN danh_muc dm ON sp.ma_danh_muc = dm.ma_danh_muc
                 LEFT JOIN nha_cung_cap ncc ON sp.ma_nha_cung_cap = ncc.ma_nha_cung_cap"""

        # Append WHERE clause to the SQL statement only if keyword is not empty
        if keyword:
            sql += """ WHERE sp.ma_san_pham LIKE %s
                       OR sp.ten_san_pham LIKE %s
                       OR dm.ten_danh_muc LIKE %s
                       OR sp.gia LIKE %s
                       OR sp.so_luong_ton LIKE %s
                       OR ncc.ten_nha_cung_cap LIKE %s"""

            search_values = tuple('%' + keyword + '%' for _ in range(6))
        else:
            search_values = ()  # Empty tuple for no parameters

            # If search box is empty, refresh the category and supplier combos also
            self.load_products()
            self.load_categories()
            self.load_suppliers()

        try:
            cursor.execute(sql, search_values)
            rows = cursor.fetchall()

            self.ui.tableSanPham.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                # Common properties
                ma_san_pham, ten_san_pham, ten_danh_muc, gia, so_luong_ton, ten_nha_cung_cap, anh = row_data

                self.ui.tableSanPham.setItem(row_idx, 0, QTableWidgetItem(str(ma_san_pham)))
                self.ui.tableSanPham.setItem(row_idx, 1, QTableWidgetItem(str(ten_san_pham)))
                self.ui.tableSanPham.setItem(row_idx, 2, QTableWidgetItem(str(ten_danh_muc)))
                self.ui.tableSanPham.setItem(row_idx, 3, QTableWidgetItem(str(gia)))
                self.ui.tableSanPham.setItem(row_idx, 4, QTableWidgetItem(str(so_luong_ton)))
                self.ui.tableSanPham.setItem(row_idx, 5, QTableWidgetItem(str(ten_nha_cung_cap or "")))

                # Xử lý cột ảnh
                image_path = anh
                if image_path:
                    try:
                        pixmap = QPixmap(image_path)
                        pixmap = pixmap.scaled(100, 75, Qt.AspectRatioMode.KeepAspectRatio)  # Correct class call
                        image_label = QLabel()
                        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  #Correct class call
                        image_label.setPixmap(pixmap)
                        self.ui.tableSanPham.setCellWidget(row_idx, 6, image_label)

                    except Exception as e:
                        print(f"Lỗi hiển thị ảnh: {e}")
                        # Hiển thị ảnh lỗi hoặc ảnh mặc định nếu có lỗi
                        default_pixmap = QPixmap("images/default_product.png")
                        default_pixmap = default_pixmap.scaled(100, 75, Qt.AspectRatioMode.KeepAspectRatio)  # Correct class call
                        image_label = QLabel()
                        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  #Correct class call
                        image_label.setPixmap(default_pixmap)
                        self.ui.tableSanPham.setCellWidget(row_idx, 6, image_label)
                else:
                    # Hiển thị ảnh mặc định nếu không có đường dẫn ảnh
                    default_pixmap = QPixmap("images/default_product.png")
                    default_pixmap = default_pixmap.scaled(100, 75, Qt.AspectRatioMode.KeepAspectRatio)  # Correct class call
                    image_label = QLabel()
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter) #Correct class call
                    image_label.setPixmap(default_pixmap)
                    self.ui.tableSanPham.setCellWidget(row_idx, 6, image_label)

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {err}")

        finally:
            cursor.close()
            conn.close()

    def export_to_excel(self):
        """Xuất dữ liệu ra file Excel"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file", "", "Excel Files (*.xlsx)")

        if not file_path:
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""SELECT sp.ma_san_pham, sp.ten_san_pham, dm.ten_danh_muc, sp.gia, sp.so_luong_ton, ncc.ten_nha_cung_cap
                        FROM san_pham sp
                        JOIN danh_muc dm ON sp.ma_danh_muc = dm.ma_danh_muc
                        LEFT JOIN nha_cung_cap ncc ON sp.ma_nha_cung_cap = ncc.ma_nha_cung_cap""")
            rows = cursor.fetchall()

            df = pd.DataFrame(rows, columns=["Mã SP", "Tên Sản Phẩm", "Danh Mục", "Giá", "Số Lượng", "Nhà Cung Cấp"]) # One less value
            df.to_excel(file_path, index=False, engine='openpyxl')

            QMessageBox.information(self, "Thành công", f"Dữ liệu đã được xuất ra file {file_path}")
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {err}")

        finally:
            cursor.close()
            conn.close()

    def is_product_in_database(self,product_id):
            conn = self.connect_db()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT 1 FROM san_pham WHERE ma_san_pham=%s", (product_id,)) #Check if the Product exist.
                return cursor.fetchone() is not None
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
                return False
            finally:
                cursor.close()
                conn.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ManageData()
    window.show()
    sys.exit(app.exec())