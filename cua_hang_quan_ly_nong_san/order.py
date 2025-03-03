import sys
import os
import datetime
import mysql.connector
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QInputDialog
from PySide6.QtCore import Qt, QFile, QIODevice, QDate
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader


# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "quan_ly_nong_san",
    "pool_name": "my_db_pool",
    "pool_size": 5
}

class OrderManagement(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            uifile = QFile("order.ui")  # Make sure this path is correct
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

            try:
                self.db_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
                print("Connection pool created successfully.")
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Lỗi", f"Khởi tạo Connection Pool thất bại: {err}")
                sys.exit(-1)

            self.ui.btnSearchProduct.clicked.connect(self.search_products)
            self.ui.btnRemoveFromCart.clicked.connect(self.remove_from_cart)
            self.ui.btnCheckout.clicked.connect(self.checkout)

            self.setup_product_table()
            self.setup_cart_table()

            self.load_products()
            self.load_customers()
            self.load_promotions()

            self.ui.txtTotal.setText("0.00")

            self.ui.cmbPromotion.currentIndexChanged.connect(self.update_total_with_discount)
            self.ui.cmbCustomer.currentIndexChanged.connect(self.customer_selection_changed)

            # Initialize customer carts and current customer
            self.customer_carts = {}
            self.current_customer_id_value = None

            # Connect the itemDoubleClicked signal of the cart table to the edit_cart_item method
            self.ui.tableCart.itemDoubleClicked.connect(self.edit_cart_item)

            self.show()

        except Exception as err:
            print(f"An error occurred during initialization: {err}")
            sys.exit(-1)

    def connect_db(self):
        try:
            conn = self.db_pool.get_connection()
            return conn
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Không thể lấy kết nối từ pool: {err}")
            return None

    def setup_product_table(self):
        self.ui.tableProducts.setColumnCount(6)
        self.ui.tableProducts.setHorizontalHeaderLabels(["Mã SP", "Tên SP", "Giá", "Số Lượng Tồn", "Đơn Vị", "Ảnh"])
        header = self.ui.tableProducts.horizontalHeader()
        for col in range(self.ui.tableProducts.columnCount() - 1):
            header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        self.ui.tableProducts.setStyleSheet("QTableWidget::item { text-align: center; }")
        self.ui.tableProducts.verticalHeader().setDefaultSectionSize(80)
        self.ui.tableProducts.itemDoubleClicked.connect(self.add_to_cart)

    def setup_cart_table(self):
        self.ui.tableCart.setColumnCount(6)
        self.ui.tableCart.setHorizontalHeaderLabels(["Mã SP", "Tên SP", "Giá", "Số Lượng", "Đơn Vị", "Tổng"])
        header = self.ui.tableCart.horizontalHeader()
        for col in range(self.ui.tableCart.columnCount() - 1):
            header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.ui.tableCart.setStyleSheet("QTableWidget::item { text-align: center; }")
        self.ui.tableCart.verticalHeader().setDefaultSectionSize(80)

    def load_products(self):
        conn = self.connect_db()
        if conn is None:
            return
        cursor = conn.cursor()
        try:
            sql = "SELECT ma_san_pham, ten_san_pham, gia, so_luong_ton, don_vi, anh FROM san_pham"
            cursor.execute(sql)
            products = cursor.fetchall()
            self.ui.tableProducts.setRowCount(len(products))

            for row, product in enumerate(products):
                self.ui.tableProducts.setItem(row, 0, QTableWidgetItem(str(product[0])))
                self.ui.tableProducts.setItem(row, 1, QTableWidgetItem(product[1]))
                self.ui.tableProducts.setItem(row, 2, QTableWidgetItem(str(product[2])))
                self.ui.tableProducts.setItem(row, 3, QTableWidgetItem(str(product[3])))
                self.ui.tableProducts.setItem(row, 4, QTableWidgetItem(product[4]))

                image_path = product[5]
                if image_path and os.path.exists(image_path):
                    pixmap = QPixmap(image_path).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
                    image_label = QtWidgets.QLabel()
                    image_label.setPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.ui.tableProducts.setCellWidget(row, 5, image_label)
                else:
                    default_pixmap = QPixmap("default_image.png").scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
                    default_label = QtWidgets.QLabel()
                    default_label.setPixmap(default_pixmap)
                    default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.ui.tableProducts.setCellWidget(row, 5, default_label)

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def GetVIPInformation(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            sql = """SELECT o.ma_khach_hang, kh.ten_kh, SUM(o.tong_tien) AS total_spent, COUNT(o.ma_order) AS total_orders
                    FROM `order` o
                    JOIN khach_hang kh ON o.ma_khach_hang = kh.ma_kh
                    GROUP BY o.ma_khach_hang, kh.ten_kh
                    HAVING SUM(o.tong_tien) > 1000000
                    ORDER BY total_spent DESC
                    LIMIT 10"""
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
        except Exception as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi load Khach hàng VIP: {err}")
            return None
        finally:
            cursor.close()
            conn.close()

    def load_customers(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            vip_customers = self.GetVIPInformation()
            cursor.execute("SELECT ma_kh, ten_kh FROM khach_hang")
            customers = cursor.fetchall()
            self.ui.cmbCustomer.clear()
            self.ui.cmbCustomer.addItem("", None)
            for customer in customers:
                ma_kh, ten_kh = customer
                display_name = ten_kh
                if vip_customers:
                    for vip_data in vip_customers:
                        if ma_kh == vip_data[0]:
                            display_name += " (VIP)"
                            break
                self.ui.cmbCustomer.addItem(display_name, ma_kh)

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        except Exception as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi: {err}")
        finally:
            cursor.close()
            conn.close()

    def load_promotions(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            current_date = datetime.date.today() # Get current date
            model = QtGui.QStandardItemModel() # Create a model to hold the data
            self.ui.cmbPromotion.setModel(model)  # Set the model for the combobox

            sql = "SELECT ma_km, ten_ma_km, phan_tram_giam, don_toi_thieu, ngay_ket_thuc_km FROM khuyen_mai"
            cursor.execute(sql)
            promotions = cursor.fetchall()

            model.appendRow(QtGui.QStandardItem(""))  # Add an empty item

            for promotion in promotions:
                ma_km, ten_ma_km, phan_tram_giam, don_toi_thieu, ngay_ket_thuc_km = promotion
                end_date = ngay_ket_thuc_km

                # Disable promotion item if end date is in the past
                if current_date > end_date:
                    item = QtGui.QStandardItem(f"{ten_ma_km} (Hết hạn)")
                    item.setEnabled(False) # Disable item to prevent interaction
                    model.appendRow(item) # append item to the QStandardItemModel
                    model.setItemData(item.index(), {QtCore.Qt.ItemDataRole.UserRole: ma_km}) #Set UserRole
                else:
                    item = QtGui.QStandardItem(f"{ten_ma_km} ({phan_tram_giam}% off, min order: {don_toi_thieu})") #create the Item to append to the model
                    model.appendRow(item)  #append item to model
                    model.setItemData(item.index(), {QtCore.Qt.ItemDataRole.UserRole: ma_km}) #set the UserRole to the item
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        except Exception as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi: {err}")
        finally:
            cursor.close()
            conn.close()

    def search_products(self):
        keyword = self.ui.txtSearchProduct.text().strip()

        if not keyword:
            self.load_products()  # Load all products if the search box is empty
            self.load_customers() # Refresh customers list
            self.load_promotions() # Refresh promotions list
            return

        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            sql = """SELECT ma_san_pham, ten_san_pham, gia, so_luong_ton, don_vi, anh
                     FROM san_pham
                     WHERE ma_san_pham LIKE %s
                        OR ten_san_pham LIKE %s"""

            cursor.execute(sql, tuple('%' + keyword + '%' for _ in range(2)))
            products = cursor.fetchall()
            self.ui.tableProducts.setRowCount(len(products))

            for row, product in enumerate(products):
                self.ui.tableProducts.setItem(row, 0, QTableWidgetItem(str(product[0])))
                self.ui.tableProducts.setItem(row, 1, QTableWidgetItem(product[1]))
                self.ui.tableProducts.setItem(row, 2, QTableWidgetItem(str(product[2])))
                self.ui.tableProducts.setItem(row, 3, QTableWidgetItem(str(product[3])))
                self.ui.tableProducts.setItem(row, 4, QTableWidgetItem(product[4]))

                image_path = product[5]
                if image_path and os.path.exists(image_path):
                    pixmap = QPixmap(image_path).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
                    image_label = QtWidgets.QLabel()
                    image_label.setPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.ui.tableProducts.setCellWidget(row, 5, image_label)
                else:
                    default_pixmap = QPixmap("default_image.png").scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
                    default_label = QtWidgets.QLabel()
                    default_label.setPixmap(default_pixmap)
                    default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.ui.tableProducts.setCellWidget(row, 5, default_label)

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
        finally:
            cursor.close()
            conn.close()

    def add_to_cart(self, item):
        # Check if a customer is selected
        if self.ui.cmbCustomer.currentIndex() == 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một khách hàng trước khi thêm sản phẩm vào giỏ hàng!")
            return

        row = item.row()
        product_id = self.ui.tableProducts.item(row, 0).text()
        name = self.ui.tableProducts.item(row, 1).text()
        price_per_unit = float(self.ui.tableProducts.item(row, 2).text())
        so_luong_ton = float(self.ui.tableProducts.item(row, 3).text())
        don_vi = self.ui.tableProducts.item(row, 4).text()

        quantity_str, ok = QInputDialog.getText(self, "Nhập số lượng", f"Nhập số lượng {name} ({don_vi}):")

        if ok and quantity_str:
            try:
                quantity = float(quantity_str)

                if don_vi in ("quả", "con"):
                    if quantity != int(quantity) or quantity <= 0:
                        QMessageBox.critical(self, "Lỗi", f"Số lượng ({don_vi}) phải là số nguyên dương!");
                        return
                    quantity = int(quantity)

                if quantity > so_luong_ton:
                    QMessageBox.critical(self, "Lỗi", f"Vượt quá số lượng tồn kho ({so_luong_ton} {don_vi})!");
                    return
                 # Get the current customer ID
                customer_id = self.ui.cmbCustomer.itemData(self.ui.cmbCustomer.currentIndex())

                # Update the stock quantity in the product table
                if not self.update_stock_quantity(product_id, -quantity):
                    return  # Stop if the update fails

                # Refresh the product table to reflect the updated stock quantity
                self.load_products()

                # Get the current customer's cart or create one if it doesn't exist
                if customer_id not in self.customer_carts:
                    self.customer_carts[customer_id] = []
                cart = self.customer_carts[customer_id]

                # Check if the product is already in the cart
                existing_item = next((item for item in cart if item['ma_san_pham'] == product_id), None)

                if existing_item:
                    new_quantity = float(existing_item['so_luong']) + quantity
                    if new_quantity > so_luong_ton:
                        # Restore the stock quantity if the new quantity is too high
                        self.update_stock_quantity(product_id, quantity)
                        self.load_products()
                        QMessageBox.critical(self, "Lỗi", f"Vượt quá số lượng tồn kho ({so_luong_ton} {don_vi})!");
                        return
                    existing_item['so_luong'] = str(new_quantity)
                    existing_item['tong'] = str(price_per_unit * new_quantity)
                    self.update_cart_table_from_customer_carts(customer_id)  # Refresh the cart table
                else:
                    # Add the product to the cart
                    item = {
                        'ma_san_pham': product_id,
                        'ten_san_pham': name,
                        'gia': str(price_per_unit),
                        'so_luong': str(quantity),
                        'don_vi': don_vi,
                        'tong': str(price_per_unit * quantity)
                    }
                    cart.append(item)
                    self.update_cart_table_from_customer_carts(customer_id) # Refresh the cart table

                self.calculate_total()
                self.update_total_with_discount()

            except ValueError:
                QMessageBox.critical(self, "Lỗi", "Vui lòng nhập số hợp lệ!");

    def update_cart_table_from_customer_carts(self, customer_id):
        """Updates the cart table to reflect the current state of the customer's cart."""
        self.ui.tableCart.setRowCount(0)  # Clear the cart table
        if customer_id in self.customer_carts:
            cart_data = self.customer_carts[customer_id]
            for item in cart_data:
                self.add_to_cart_table(
                    item['ma_san_pham'],
                    item['ten_san_pham'],
                    float(item['gia']),
                    float(item['so_luong']),
                    item['don_vi'],
                    float(item['tong'])
                )

    def find_product_in_cart(self, product_id):
        for row in range(self.ui.tableCart.rowCount()):
            if self.ui.tableCart.item(row, 0).text() == product_id:
                return row
        return None

    def add_to_cart_table(self, product_id, name, price, quantity, don_vi, total):
        rowPosition = self.ui.tableCart.rowCount()
        self.ui.tableCart.insertRow(rowPosition)
        self.ui.tableCart.setItem(rowPosition, 0, QTableWidgetItem(str(product_id)))
        self.ui.tableCart.setItem(rowPosition, 1, QTableWidgetItem(str(name)))
        self.ui.tableCart.setItem(rowPosition, 2, QTableWidgetItem(str(price)))
        self.ui.tableCart.setItem(rowPosition, 3, QTableWidgetItem(str(quantity)))
        self.ui.tableCart.setItem(rowPosition, 4, QTableWidgetItem(str(don_vi)))
        self.ui.tableCart.setItem(rowPosition, 5, QTableWidgetItem(str(total)))

    def remove_from_cart(self):
        selected_row = self.ui.tableCart.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn sản phẩm để xóa!");
            return

        # Get the product ID and quantity from the selected row
        product_id = self.ui.tableCart.item(selected_row, 0).text()
        quantity = float(self.ui.tableCart.item(selected_row, 3).text())

        # Get the current customer ID
        customer_id = self.ui.cmbCustomer.itemData(self.ui.cmbCustomer.currentIndex())

        if customer_id and customer_id in self.customer_carts:
            # Find the item in the customer's cart
            cart = self.customer_carts[customer_id]
            item_to_remove = next((item for item in cart if item['ma_san_pham'] == product_id), None)

            if item_to_remove:
                # Restore the stock quantity
                if not self.update_stock_quantity(product_id, quantity):
                    return  # Stop if the update fails

                # Remove the item from the cart
                self.customer_carts[customer_id] = [item for item in cart if item['ma_san_pham'] != product_id]

                # Refresh the cart table and product table
                self.update_cart_table_from_customer_carts(customer_id)
                self.load_products()
                self.calculate_total()
                self.update_total_with_discount()
            else:
                QMessageBox.warning(self, "Lỗi", "Sản phẩm không tồn tại trong giỏ hàng!");
        else:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy giỏ hàng cho khách hàng hiện tại!");

    def calculate_total(self):
        total = 0
        for row in range(self.ui.tableCart.rowCount()):
            price_str = self.ui.tableCart.item(row, 2).text()
            quantity_str = self.ui.tableCart.item(row, 3).text()
            try:
                price = float(price_str)
                quantity = float(quantity_str)
                total += price * quantity
            except ValueError:
                QMessageBox.warning(self, "Lỗi", f"Invalid price or quantity at row {row + 1}!")
                return
        return total

    def checkout(self):
        customer_id = self.ui.cmbCustomer.itemData(self.ui.cmbCustomer.currentIndex())
        promotion_id = self.ui.cmbPromotion.itemData(self.ui.cmbPromotion.currentIndex())
        total = self.calculate_total()
        discount = 0

        if self.ui.tableCart.rowCount() == 0:
            QMessageBox.warning(self, "Lỗi", "Giỏ hàng trống!");
            return

        if customer_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khách hàng!");
            return

        if promotion_id is not None:
            discount, can_apply = self.apply_discount(total, promotion_id)
            if not can_apply:
                return

        final_total = total - discount

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            sql_order = "INSERT INTO `order` (ma_khach_hang, ma_khuyen_mai, tong_tien) VALUES (%s, %s, %s)"
            values_order = (customer_id, promotion_id, final_total)
            cursor.execute(sql_order, values_order)
            conn.commit()
            order_id = cursor.lastrowid

            # Get the cart data from customer_carts
            if customer_id in self.customer_carts:
                cart_data = self.customer_carts[customer_id]
            else:
                QMessageBox.warning(self, "Lỗi", "Giỏ hàng không tồn tại!");
                return

            sql_detail = """INSERT INTO order_detail (ma_order, ma_san_pham, so_luong, gia_ban)
                            VALUES (%s, %s, %s, %s)"""

            for item in cart_data:
                ma_san_pham = item['ma_san_pham']
                so_luong = float(item['so_luong'])
                gia_ban = float(item['gia'])

                val_detail = (order_id, ma_san_pham, so_luong, gia_ban)
                cursor.execute(sql_detail, val_detail)

            conn.commit()

            QMessageBox.information(self, "Thành công", "Thanh toán thành công!")

            # Clear the cart data after checkout
            self.clear_cart_information()
            if customer_id in self.customer_carts:
                del self.customer_carts[customer_id]
            self.load_products()
            self.update_cart_table_from_customer_carts(customer_id)


        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
            conn.rollback()  # Rollback in case of error
        finally:
            cursor.close()
            conn.close()

    def edit_cart_item(self, item):
        if item.column() == 3:  # Số Lượng column
            row = item.row()
            product_id = self.ui.tableCart.item(row, 0).text()
            name = self.ui.tableCart.item(row, 1).text()
            price_per_unit = float(self.ui.tableCart.item(row, 2).text())
            don_vi = self.ui.tableCart.item(row, 4).text()

            # Get current stock quantity from the product table
            stock_quantity = self.get_stock_quantity(product_id)
            if stock_quantity is None:
                QMessageBox.critical(self, "Lỗi", "Không thể lấy số lượng tồn kho của sản phẩm.");
                return

            current_quantity = float(item.text())
            quantity_str, ok = QInputDialog.getText(self, "Chỉnh sửa số lượng", f"Nhập số lượng mới cho {name} ({don_vi}):", text=str(current_quantity))

            if ok and quantity_str:
                try:
                    new_quantity = float(quantity_str)

                    if don_vi in ("quả", "con"):
                        if new_quantity != int(new_quantity) or new_quantity <= 0:
                            QMessageBox.critical(self, "Lỗi", f"Số lượng ({don_vi}) phải là số nguyên dương!");
                            return
                        new_quantity = int(new_quantity)

                    customer_id = self.ui.cmbCustomer.itemData(self.ui.cmbCustomer.currentIndex())
                    if customer_id and customer_id in self.customer_carts:
                        cart = self.customer_carts[customer_id]
                        existing_item = next((item for item in cart if item['ma_san_pham'] == product_id), None)

                        if existing_item:
                            # Calculate available stock: current stock + quantity in cart
                            available_stock = stock_quantity + current_quantity

                            if new_quantity > available_stock:
                                QMessageBox.critical(self, "Lỗi", f"Vượt quá số lượng tồn kho ({available_stock} {don_vi})!");
                                return

                            # Adjust stock quantity: first restore old quantity, then subtract new quantity
                            quantity_difference = current_quantity - new_quantity
                            if not self.update_stock_quantity(product_id, quantity_difference):
                                return  # Stop if the update fails

                            existing_item['so_luong'] = str(new_quantity)
                            existing_item['tong'] = str(price_per_unit * new_quantity)
                            self.update_cart_table_from_customer_carts(customer_id)  # Refresh the cart table

                        else:
                            QMessageBox.critical(self, "Lỗi", "Không tìm thấy sản phẩm trong giỏ hàng!");
                    else:
                        QMessageBox.critical(self, "Lỗi", "Không tìm thấy giỏ hàng cho khách hàng hiện tại!");

                    # Recalculate total and update discount
                    self.load_products() # Refresh products table
                    self.calculate_total()
                    self.update_total_with_discount()

                except ValueError:
                    QMessageBox.critical(self, "Lỗi", "Vui lòng nhập số hợp lệ!");

    def get_stock_quantity(self, product_id):
        conn = self.connect_db()
        if conn is None:
            return None
        cursor = conn.cursor()
        try:
            sql = "SELECT so_luong_ton FROM san_pham WHERE ma_san_pham = %s"
            cursor.execute(sql, (product_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
            return None
        finally:
            cursor.close()
            conn.close()

    def update_stock_quantity(self, product_id, quantity_change):
        """Updates the stock quantity in the database."""
        conn = self.connect_db()
        if conn is None:
            return False
        cursor = conn.cursor()
        try:
            sql = "UPDATE san_pham SET so_luong_ton = so_luong_ton + %s WHERE ma_san_pham = %s"
            val = (quantity_change, product_id)
            cursor.execute(sql, val)
            conn.commit()
            return True
        except mysql.connector.Error as err:
            conn.rollback()  # Rollback in case of error
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL khi cập nhật số lượng tồn kho: {err}")
            return False
        finally:
            cursor.close()
            conn.close()

    def clear_cart_information(self):
        self.ui.tableCart.setRowCount(0)
        self.ui.txtTotal.setText("0.00")

    def apply_discount(self, total, promotion_id):
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            current_date = datetime.date.today() # Get current date
            sql = "SELECT phan_tram_giam, don_toi_thieu, ngay_ket_thuc_km FROM khuyen_mai WHERE ma_km = %s"
            cursor.execute(sql, (promotion_id,))
            promotion = cursor.fetchone()

            if promotion:
                phan_tram_giam, don_toi_thieu, ngay_ket_thuc_km = promotion

                if current_date > ngay_ket_thuc_km: # if promotion is expired then return
                     QMessageBox.information(self, "Thông báo", "Mã khuyến mãi đã hết hạn.")
                     return 0, False

                if total < float(don_toi_thieu):
                    QMessageBox.information(self, "Thông báo", f"Đơn hàng chưa đạt giá trị tối thiểu để áp dụng mã khuyến mãi này! (Tối thiểu: {don_toi_thieu})")
                    return 0, False

                discount = total * phan_tram_giam / 100
                return discount, True
            else:
                QMessageBox.critical(self, "Lỗi", "Mã khuyến mãi không hợp lệ!")
                return 0, False
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi", f"Lỗi MySQL: {err}")
            return 0, False
        finally:
            cursor.close()
            conn.close()

    def update_total_with_discount(self):
        total = self.calculate_total()
        promotion_id = self.ui.cmbPromotion.itemData(self.ui.cmbPromotion.currentIndex())

        if promotion_id is not None:
            discount, can_apply = self.apply_discount(total, promotion_id)
            if can_apply:
                final_total = total - discount
                self.ui.txtTotal.setText(f"{final_total:.2f}")
            else:
                self.ui.txtTotal.setText(f"{total:.2f}")
        else:
            self.ui.txtTotal.setText(f"{total:.2f}")

    def customer_selection_changed(self, index):
        customer_id = self.ui.cmbCustomer.itemData(index)

        current_customer_id = self.current_customer_id()
        if current_customer_id:
            self.save_cart(current_customer_id)

        self.load_cart(customer_id)
        self.update_total_with_discount()

        self.current_customer_id_value = customer_id


    def save_cart(self, customer_id):
        cart_data = []
        for row in range(self.ui.tableCart.rowCount()):
            item = {}
            item['ma_san_pham'] = self.ui.tableCart.item(row, 0).text()
            item['ten_san_pham'] = self.ui.tableCart.item(row, 1).text()
            item['gia'] = self.ui.tableCart.item(row, 2).text()
            item['so_luong'] = self.ui.tableCart.item(row, 3).text()
            item['don_vi'] = self.ui.tableCart.item(row, 4).text()
            item['tong'] = self.ui.tableCart.item(row, 5).text()
            cart_data.append(item)
        self.customer_carts[customer_id] = cart_data

    def load_cart(self, customer_id):
        self.clear_cart_information()

        if customer_id in self.customer_carts:
            cart_data = self.customer_carts[customer_id]
            for item in cart_data:
                self.add_to_cart_table(
                    item['ma_san_pham'],
                    item['ten_san_pham'],
                    float(item['gia']),
                    float(item['so_luong']),
                    item['don_vi'],
                    float(item['tong'])
                )
        else:
            # Create an empty customer value if it's not exist.
            self.customer_carts[customer_id] = []

        self.calculate_total()
        self.update_total_with_discount()
    def current_customer_id(self):
        return self.current_customer_id_value if hasattr(self, 'current_customer_id_value') else None

    def clear_cart_information(self):
        self.ui.tableCart.setRowCount(0)
        self.ui.txtTotal.setText("0.00")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = OrderManagement()
    sys.exit(app.exec())