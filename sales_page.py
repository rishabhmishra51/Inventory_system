"""
sales_page.py - Sales recording and listing page.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QComboBox, QDoubleSpinBox, QSpinBox, QMessageBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate

import database as db


class SaleDialog(QDialog):
    """Dialog for recording a new sale."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💰  Record Sale")
        self.setMinimumWidth(420)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        self.product_combo = QComboBox()
        products = db.get_all_products()
        self.prod_map = {}
        for p in products:
            label = f"{p[1]} (SKU: {p[2]}) — Qty: {p[6]} — ₹{p[4]:,.2f}"
            self.product_combo.addItem(label, p[0])
            self.prod_map[p[0]] = p
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)
        layout.addRow("Product", self.product_combo)

        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 9999999)
        self.qty_input.setValue(1)
        self.qty_input.valueChanged.connect(self.update_total)
        layout.addRow("Quantity", self.qty_input)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 9999999)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("₹ ")
        self.price_input.valueChanged.connect(self.update_total)
        layout.addRow("Sale Price (each)", self.price_input)

        self.total_label = QLabel("₹ 0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0f9d58;")
        layout.addRow("Total", self.total_label)

        # Trigger initial price
        self.on_product_changed()

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💰  Record Sale")
        save_btn.setObjectName("successBtn")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("outlineBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)

    def on_product_changed(self):
        pid = self.product_combo.currentData()
        if pid and pid in self.prod_map:
            self.price_input.setValue(self.prod_map[pid][4])
        self.update_total()

    def update_total(self):
        total = self.qty_input.value() * self.price_input.value()
        self.total_label.setText(f"₹ {total:,.2f}")

    def save(self):
        product_id = self.product_combo.currentData()
        qty = self.qty_input.value()
        price = self.price_input.value()

        if product_id is None:
            QMessageBox.warning(self, "Error", "Please select a product.")
            return

        product = self.prod_map.get(product_id)
        if product and qty > product[6]:
            QMessageBox.warning(
                self, "Insufficient Stock",
                f"Only {product[6]} units available."
            )
            return

        try:
            db.record_sale(product_id, qty, price)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class SalesPage(QWidget):
    """Sales page with history and recording."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("💰  Sales")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        # Date filters
        header.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        header.addWidget(self.date_from)

        header.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        header.addWidget(self.date_to)

        filter_btn = QPushButton("🔍  Filter")
        filter_btn.setObjectName("outlineBtn")
        filter_btn.clicked.connect(self.apply_filter)
        header.addWidget(filter_btn)

        sale_btn = QPushButton("💰  New Sale")
        sale_btn.setObjectName("successBtn")
        sale_btn.clicked.connect(self.new_sale)
        header.addWidget(sale_btn)

        layout.addLayout(header)

        # Summary row
        self.summary_layout = QHBoxLayout()
        self.summary_layout.setSpacing(16)
        layout.addLayout(self.summary_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Product", "Qty Sold", "Price", "Total", "Date"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def refresh(self):
        self._load_sales(db.get_sales())

    def _load_sales(self, sales):
        self.table.setRowCount(0)
        total_revenue = 0
        total_units = 0

        for s in sales:
            row = self.table.rowCount()
            self.table.insertRow(row)
            items = [str(s[0]), s[1], str(s[2]),
                     f"₹{s[3]:,.2f}", f"₹{s[4]:,.2f}", s[5][:16]]
            total_revenue += s[4]
            total_units += s[2]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

        # Update summary
        while self.summary_layout.count():
            child = self.summary_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for label_text, value, color in [
            ("Total Sales", str(len(sales)), "#1a73e8"),
            ("Units Sold", str(total_units), "#8e24aa"),
            ("Revenue", f"₹{total_revenue:,.2f}", "#0f9d58"),
        ]:
            frame = QLabel(f"  {label_text}: {value}  ")
            frame.setStyleSheet(f"""
                background: {color}; color: white; padding: 8px 16px;
                border-radius: 4px; font-weight: bold; font-size: 13px;
            """)
            self.summary_layout.addWidget(frame)
        self.summary_layout.addStretch()

    def apply_filter(self):
        start = self.date_from.date().toString("yyyy-MM-dd") + " 00:00:00"
        end = self.date_to.date().toString("yyyy-MM-dd") + " 23:59:59"
        self._load_sales(db.get_sales(start, end))

    def new_sale(self):
        dlg = SaleDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.refresh()
