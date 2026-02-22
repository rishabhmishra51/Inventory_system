"""
stock_page.py - Stock tracking page with stock-in / stock-out and movement history.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QComboBox, QSpinBox, QTextEdit, QMessageBox, QFrame, QTabWidget
)
from PyQt5.QtCore import Qt

import database as db


class StockMovementDialog(QDialog):
    """Dialog for adding stock in or out."""

    def __init__(self, parent=None, movement_type="IN"):
        super().__init__(parent)
        self.movement_type = movement_type
        title = "📥  Stock In" if movement_type == "IN" else "📤  Stock Out"
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        self.product_combo = QComboBox()
        products = db.get_all_products()
        self.prod_map = {}
        for p in products:
            label = f"{p[1]} (SKU: {p[2]}) — Qty: {p[6]}"
            self.product_combo.addItem(label, p[0])
            self.prod_map[p[0]] = p
        layout.addRow("Product", self.product_combo)

        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 9999999)
        self.qty_input.setValue(1)
        layout.addRow("Quantity", self.qty_input)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(60)
        self.note_input.setPlaceholderText("Optional note")
        layout.addRow("Note", self.note_input)

        btn_layout = QHBoxLayout()
        color = "successBtn" if self.movement_type == "IN" else "dangerBtn"
        emoji = "📥" if self.movement_type == "IN" else "📤"
        save_btn = QPushButton(f"{emoji}  Confirm")
        save_btn.setObjectName(color)
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("outlineBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)

    def save(self):
        product_id = self.product_combo.currentData()
        qty = self.qty_input.value()
        note = self.note_input.toPlainText().strip()

        if product_id is None:
            QMessageBox.warning(self, "Error", "Please select a product.")
            return

        if self.movement_type == "OUT":
            product = self.prod_map.get(product_id)
            if product and qty > product[6]:
                QMessageBox.warning(
                    self, "Insufficient Stock",
                    f"Only {product[6]} units available in stock."
                )
                return

        try:
            if self.movement_type == "IN":
                db.add_stock_in(product_id, qty, note)
            else:
                db.add_stock_out(product_id, qty, note)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class StockPage(QWidget):
    """Stock tracking page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("📦  Stock Management")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        stock_in_btn = QPushButton("📥  Stock In")
        stock_in_btn.setObjectName("successBtn")
        stock_in_btn.clicked.connect(self.stock_in)
        header.addWidget(stock_in_btn)

        stock_out_btn = QPushButton("📤  Stock Out")
        stock_out_btn.setObjectName("dangerBtn")
        stock_out_btn.clicked.connect(self.stock_out)
        header.addWidget(stock_out_btn)

        layout.addLayout(header)

        # Tabs
        tabs = QTabWidget()

        # Current stock tab
        stock_widget = QWidget()
        stock_layout = QVBoxLayout(stock_widget)
        stock_layout.setContentsMargins(0, 12, 0, 0)

        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(7)
        self.stock_table.setHorizontalHeaderLabels([
            "ID", "Product", "SKU", "Category", "Qty", "Threshold", "Status"
        ])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stock_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.stock_table.setAlternatingRowColors(True)
        stock_layout.addWidget(self.stock_table)
        tabs.addTab(stock_widget, "📊  Current Stock")

        # Movement history tab
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 12, 0, 0)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Product", "Type", "Quantity", "Note", "Date"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setAlternatingRowColors(True)
        history_layout.addWidget(self.history_table)
        tabs.addTab(history_widget, "📋  Movement History")

        # Low stock alerts tab
        alerts_widget = QWidget()
        alerts_layout = QVBoxLayout(alerts_widget)
        alerts_layout.setContentsMargins(0, 12, 0, 0)

        alert_banner = QLabel("⚠️  These products are at or below their low stock threshold. Restock immediately!")
        alert_banner.setStyleSheet("""
            background-color: #fce8e6; color: #c5221f; padding: 12px;
            border-radius: 4px; font-weight: bold;
        """)
        alerts_layout.addWidget(alert_banner)

        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels([
            "Product", "SKU", "Category", "Current Qty", "Threshold"
        ])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alerts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alerts_table.setSelectionBehavior(QTableWidget.SelectRows)
        alerts_layout.addWidget(self.alerts_table)
        tabs.addTab(alerts_widget, "🔔  Low Stock Alerts")

        layout.addWidget(tabs)

    def refresh(self):
        self._load_stock()
        self._load_history()
        self._load_alerts()

    def _load_stock(self):
        self.stock_table.setRowCount(0)
        products = db.get_all_products()
        for p in products:
            row = self.stock_table.rowCount()
            self.stock_table.insertRow(row)
            status = "✅ OK" if p[6] > p[7] else "⚠️ LOW"
            items = [str(p[0]), p[1], p[2], p[3] or "N/A",
                     str(p[6]), str(p[7]), status]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 6 and p[6] <= p[7]:
                    item.setForeground(Qt.red)
                if col == 4 and p[6] <= p[7]:
                    item.setForeground(Qt.red)
                self.stock_table.setItem(row, col, item)

    def _load_history(self):
        self.history_table.setRowCount(0)
        movements = db.get_stock_movements()
        for m in movements:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            items = [str(m[0]), m[1], m[2], str(m[3]), m[4] or "", m[5][:16]]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 2:
                    if m[2] == "IN":
                        item.setForeground(Qt.darkGreen)
                    else:
                        item.setForeground(Qt.red)
                self.history_table.setItem(row, col, item)

    def _load_alerts(self):
        self.alerts_table.setRowCount(0)
        low = db.get_low_stock_products()
        for p in low:
            row = self.alerts_table.rowCount()
            self.alerts_table.insertRow(row)
            items = [p[1], p[2], p[3] or "N/A", str(p[6]), str(p[7])]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 3:
                    item.setForeground(Qt.red)
                self.alerts_table.setItem(row, col, item)

    def stock_in(self):
        dlg = StockMovementDialog(self, "IN")
        if dlg.exec_() == QDialog.Accepted:
            self.refresh()

    def stock_out(self):
        dlg = StockMovementDialog(self, "OUT")
        if dlg.exec_() == QDialog.Accepted:
            self.refresh()
