from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox
from ui.product_form import ProductForm
from ui.sales_form import SalesForm
from services.inventory_service import get_low_stock
from services.report_service import export_products_csv

class Dashboard(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Inventory System")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        btn_product = QPushButton("Manage Products")
        btn_sales = QPushButton("Record Sale")
        btn_low = QPushButton("Low Stock Alerts")
        btn_export = QPushButton("Export CSV")

        btn_product.clicked.connect(self.open_products)
        btn_sales.clicked.connect(self.open_sales)
        btn_low.clicked.connect(self.show_low_stock)
        btn_export.clicked.connect(export_products_csv)

        layout.addWidget(btn_product)
        layout.addWidget(btn_sales)
        layout.addWidget(btn_low)
        layout.addWidget(btn_export)

        self.setLayout(layout)

    def open_products(self):
        self.product_window = ProductForm()
        self.product_window.show()

    def open_sales(self):
        self.sales_window = SalesForm()
        self.sales_window.show()

    def show_low_stock(self):
        items = get_low_stock()
        if items:
            QMessageBox.warning(self, "Low Stock Alert", str(items))
        else:
            QMessageBox.information(self, "Stock OK", "No low stock items")