"""
products_page.py - Product management page with CRUD operations.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QComboBox, QDoubleSpinBox, QSpinBox, QTextEdit, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt

import database as db


class ProductDialog(QDialog):
    """Dialog for adding / editing a product."""

    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Edit Product" if product else "Add New Product")
        self.setMinimumWidth(450)
        self.setup_ui()
        if product:
            self.populate(product)

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product name")
        layout.addRow("Name *", self.name_input)

        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Unique SKU code")
        layout.addRow("SKU *", self.sku_input)

        self.category_combo = QComboBox()
        categories = db.get_categories()
        self.cat_map = {}
        for cat_id, cat_name in categories:
            self.category_combo.addItem(cat_name, cat_id)
            self.cat_map[cat_id] = cat_name
        layout.addRow("Category", self.category_combo)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 9999999)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("₹ ")
        layout.addRow("Sell Price *", self.price_input)

        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 9999999)
        self.cost_input.setDecimals(2)
        self.cost_input.setPrefix("₹ ")
        layout.addRow("Cost Price", self.cost_input)

        self.qty_input = QSpinBox()
        self.qty_input.setRange(0, 9999999)
        layout.addRow("Quantity", self.qty_input)

        self.threshold_input = QSpinBox()
        self.threshold_input.setRange(0, 9999999)
        self.threshold_input.setValue(10)
        layout.addRow("Low Stock Threshold", self.threshold_input)

        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.desc_input.setPlaceholderText("Optional description")
        layout.addRow("Description", self.desc_input)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾  Save")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("outlineBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)

    def populate(self, p):
        # p: id, name, sku, cat_name, price, cost, qty, threshold, desc, created, updated, cat_id
        self.name_input.setText(p[1])
        self.sku_input.setText(p[2])
        idx = self.category_combo.findData(p[11])
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
        self.price_input.setValue(p[4])
        self.cost_input.setValue(p[5])
        self.qty_input.setValue(p[6])
        self.threshold_input.setValue(p[7])
        self.desc_input.setPlainText(p[8] or "")

    def save(self):
        name = self.name_input.text().strip()
        sku = self.sku_input.text().strip()
        if not name or not sku:
            QMessageBox.warning(self, "Validation", "Name and SKU are required.")
            return

        cat_id = self.category_combo.currentData()
        price = self.price_input.value()
        cost = self.cost_input.value()
        qty = self.qty_input.value()
        threshold = self.threshold_input.value()
        desc = self.desc_input.toPlainText().strip()

        try:
            if self.product:
                db.update_product(self.product[0], name, sku, cat_id, price,
                                  cost, qty, threshold, desc)
            else:
                db.add_product(name, sku, cat_id, price, cost, qty, threshold, desc)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ProductsPage(QWidget):
    """Products listing and management page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("📦  Products")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search products...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.on_search)
        header.addWidget(self.search_input)

        add_btn = QPushButton("➕  Add Product")
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self.add_product)
        header.addWidget(add_btn)

        layout.addLayout(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "SKU", "Category", "Price",
            "Cost", "Qty", "Threshold", "Updated"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.edit_product)
        layout.addWidget(self.table)

        # Bottom buttons
        btn_bar = QHBoxLayout()
        btn_bar.addStretch()

        edit_btn = QPushButton("✏️  Edit")
        edit_btn.setObjectName("outlineBtn")
        edit_btn.clicked.connect(self.edit_product)
        btn_bar.addWidget(edit_btn)

        del_btn = QPushButton("🗑️  Delete")
        del_btn.setObjectName("dangerBtn")
        del_btn.clicked.connect(self.delete_product)
        btn_bar.addWidget(del_btn)

        layout.addLayout(btn_bar)

    def refresh(self):
        self.load_products(db.get_all_products())

    def load_products(self, products):
        self.table.setRowCount(0)
        for row_data in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            # id, name, sku, cat_name, price, cost, qty, threshold, desc, created, updated, cat_id
            display = [
                str(row_data[0]),
                row_data[1],
                row_data[2],
                row_data[3] or "N/A",
                f"₹{row_data[4]:,.2f}",
                f"₹{row_data[5]:,.2f}",
                str(row_data[6]),
                str(row_data[7]),
                row_data[10][:16] if row_data[10] else ""
            ]
            for col, val in enumerate(display):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                # Highlight low stock
                if col == 6 and row_data[6] <= row_data[7]:
                    item.setForeground(Qt.red)
                    item.setToolTip("⚠ Low stock!")
                self.table.setItem(row, col, item)

    def on_search(self, text):
        if text.strip():
            self.load_products(db.search_products(text.strip()))
        else:
            self.refresh()

    def get_selected_product_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "Select", "Please select a product first.")
            return None
        return int(self.table.item(rows[0].row(), 0).text())

    def add_product(self):
        dlg = ProductDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.refresh()

    def edit_product(self):
        pid = self.get_selected_product_id()
        if pid is None:
            return
        product = db.get_product_by_id(pid)
        if product:
            dlg = ProductDialog(self, product)
            if dlg.exec_() == QDialog.Accepted:
                self.refresh()

    def delete_product(self):
        pid = self.get_selected_product_id()
        if pid is None:
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this product and all its related records?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            db.delete_product(pid)
            self.refresh()
