from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton
from services.inventory_service import record_sale
from services.report_service import sales_summary
import matplotlib.pyplot as plt

class SalesForm(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sales Entry")

        layout = QVBoxLayout()

        self.product_id = QLineEdit()
        self.product_id.setPlaceholderText("Product ID")

        self.quantity = QLineEdit()
        self.quantity.setPlaceholderText("Quantity Sold")

        btn_record = QPushButton("Record Sale")
        btn_chart = QPushButton("Show Sales Chart")

        btn_record.clicked.connect(self.record_sale_ui)
        btn_chart.clicked.connect(self.show_chart)

        layout.addWidget(self.product_id)
        layout.addWidget(self.quantity)
        layout.addWidget(btn_record)
        layout.addWidget(btn_chart)

        self.setLayout(layout)

    def record_sale_ui(self):
        record_sale(int(self.product_id.text()),
                    int(self.quantity.text()))

    def show_chart(self):
        df = sales_summary()
        plt.bar(df["name"], df["total_sold"])
        plt.title("Sales Summary")
        plt.show()