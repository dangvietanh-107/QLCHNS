import sys
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt, QFile, QIODevice
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader

from products import ManageData
from order import OrderManagement
from users import UserManagement
from supplier import SupplierWindow  # Changed to SupplierWindow to match your supplier.py
from ui_khuyen_mai import KhuyenMaiManagement  # Assuming file is in same directory
from order_detail_window import OrderDetailWindow
from report import ReportManagement
from danh_muc import DanhMucManagement

class MenuApp(QtWidgets.QMainWindow):  # Changed to QMainWindow
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Hệ Thống Quản Lý")
        self.setGeometry(100, 100, 900, 600)
        
        # 🌟 Tạo layout chính
        main_widget = QtWidgets.QWidget(self)  # Create a central widget
        main_layout = QtWidgets.QHBoxLayout(main_widget) #Main layout add to widget
        self.setCentralWidget(main_widget) #Call here so can implement `addWidget`.
        
        # 🌟 Tạo sidebar menu
        self.menu_list = QtWidgets.QListWidget()
        self.menu_list.setFixedWidth(200)
        self.menu_list.addItem("📦 Sản phẩm")
        self.menu_list.addItem("🛒 Giao dịch")
        self.menu_list.addItem("👤 Khách hàng")
        self.menu_list.addItem("🏢 Nhà cung cấp")
        self.menu_list.addItem("📜 Danh mục")
        self.menu_list.addItem("🎉 Khuyến mãi")
        self.menu_list.addItem("📋 Lịch sử")
        self.menu_list.addItem("📊 Thông kê")
        self.menu_list.addItem("🚪 Đăng xuất")  
        
        # 🌟 Style cho menu sidebar
        self.menu_list.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50; color: white;
                font-size: 16px; border: none;
            }
            QListWidget::item {
                padding: 15px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
            }
        """)

        # 🌟 Khu vực hiển thị giao diện chính
        self.stacked_widget = QtWidgets.QStackedWidget()
        
        # 🌟 Khởi tạo các giao diện
        self.products_page = ManageData()
        self.order_page = OrderManagement()
        self.users_page = UserManagement()
        self.supplier_page = SupplierWindow()
        self.danhmuc_page = DanhMucManagement()  # Instantiate SupplierWindow
        self.khuyenmai_page = KhuyenMaiManagement()
        self.orderdetail_page = OrderDetailWindow()
        self.report_page = ReportManagement()

        self.pages = {
            0: self.products_page,
            1: self.order_page,
            2: self.users_page,
            3: self.supplier_page,
            4: self.danhmuc_page,  # Use the instantiated page
            5: self.khuyenmai_page,
            6: self.orderdetail_page,
            7: self.report_page
        }

        # 🌟 Thêm các giao diện vào `QStackedWidget`
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)

        # 🌟 Liên kết menu với giao diện
        self.menu_list.currentRowChanged.connect(self.switch_page)

        # 🌟 Chia layout thành 2 phần (menu trái + nội dung)
        main_layout.addWidget(self.menu_list)
        main_layout.addWidget(self.stacked_widget, 1)  # Phần nội dung chiếm hết khoảng trống còn lại
        
        #self.setLayout(main_layout)  # NO NO NO! - not needed
        
    def switch_page(self, index):
        """ Chuyển đổi giao diện khi chọn menu """
        if index == 8:  # Index for "Đăng xuất"
            self.logout()
        else:
            self.stacked_widget.setCurrentIndex(index)

    def logout(self):
        """ Handles the logout functionality """
        # Close the current window
        self.close()

        # Open the login window
        from login import LoginDialog  # Local import
        self.login_window = LoginDialog()
        self.login_window.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MenuApp()
    window.show()
    sys.exit(app.exec())