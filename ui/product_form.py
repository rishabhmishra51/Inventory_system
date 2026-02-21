from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit
from services.inventory_service import add_product, get_all_products, delete_product

class ProductForm(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Product Management")

        layout = QVBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText("Name")

        self.category = QLineEdit()
        self.category.setPlaceholderText("Category")

        self.quantity = QLineEdit()
        self.quantity.setPlaceholderText("Quantity")

        self.price = QLineEdit()
        self.price.setPlaceholderText("Price")

        self.threshold = QLineEdit()
        self.threshold.setPlaceholderText("Threshold")

        btn_add = QPushButton("Add")
        btn_show = QPushButton("Show All")
        btn_delete = QPushButton("Delete by ID")

        self.output = QTextEdit()

        btn_add.clicked.connect(self.add_product_ui)
        btn_show.clicked.connect(self.show_products)
        btn_delete.clicked.connect(self.delete_product_ui)

        layout.addWidget(self.name)
        layout.addWidget(self.category)
        layout.addWidget(self.quantity)
        layout.addWidget(self.price)
        layout.addWidget(self.threshold)
        layout.addWidget(btn_add)
        layout.addWidget(btn_show)
        layout.addWidget(btn_delete)
        layout.addWidget(self.output)

        self.setLayout(layout)

    def add_product_ui(self):
        add_product(
            self.name.text(),
            self.category.text(),
            int(self.quantity.text()),
            float(self.price.text()),
            int(self.threshold.text())
        )

    def show_products(self):
        products = get_all_products()
        self.output.clear()
        for p in products:
            self.output.append(str(p))

    def delete_product_ui(self):
        pid = int(self.name.text())
        delete_product(pid)