"""
dashboard.py - Dashboard / Home page showing key stats and charts.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout,
    QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import database as db


class StatCard(QFrame):
    """A small card widget that displays one metric."""

    def __init__(self, title, value, color="#1a73e8", parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setStyleSheet(f"""
            QFrame {{
                background: #ffffff;
                border: 1px solid #dadce0;
                border-radius: 8px;
                border-top: 3px solid {color};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)

        lbl_value = QLabel(str(value))
        lbl_value.setObjectName("statValue")
        lbl_value.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        lbl_value.setAlignment(Qt.AlignCenter)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("statLabel")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("color: #5f6368; font-size: 12px;")

        layout.addWidget(lbl_value)
        layout.addWidget(lbl_title)


class MiniChart(FigureCanvas):
    """Small embedded Matplotlib chart."""

    def __init__(self, width=5, height=3, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#ffffff')
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class DashboardPage(QWidget):
    """The main dashboard page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Title
        title = QLabel("📊  Dashboard")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        # Stat cards row
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(16)
        layout.addLayout(self.cards_layout)

        # Charts row
        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        # Sales chart
        sales_frame = QFrame()
        sales_frame.setStyleSheet("QFrame { background: white; border: 1px solid #dadce0; border-radius: 8px; }")
        sf_layout = QVBoxLayout(sales_frame)
        sf_layout.setContentsMargins(16, 16, 16, 16)
        sf_label = QLabel("📈  Sales (Last 30 Days)")
        sf_label.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
        sf_layout.addWidget(sf_label)
        self.sales_chart = MiniChart(5, 3)
        sf_layout.addWidget(self.sales_chart)
        charts_row.addWidget(sales_frame, stretch=3)

        # Category pie
        cat_frame = QFrame()
        cat_frame.setStyleSheet("QFrame { background: white; border: 1px solid #dadce0; border-radius: 8px; }")
        cf_layout = QVBoxLayout(cat_frame)
        cf_layout.setContentsMargins(16, 16, 16, 16)
        cf_label = QLabel("🏷️  Revenue by Category")
        cf_label.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
        cf_layout.addWidget(cf_label)
        self.cat_chart = MiniChart(4, 3)
        cf_layout.addWidget(self.cat_chart)
        charts_row.addWidget(cat_frame, stretch=2)

        layout.addLayout(charts_row)

        # Low stock table
        low_frame = QFrame()
        low_frame.setStyleSheet("QFrame { background: white; border: 1px solid #dadce0; border-radius: 8px; }")
        lf_layout = QVBoxLayout(low_frame)
        lf_layout.setContentsMargins(16, 16, 16, 16)
        lf_label = QLabel("⚠️  Low Stock Alerts")
        lf_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #db4437; border: none;")
        lf_layout.addWidget(lf_label)

        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(5)
        self.low_stock_table.setHorizontalHeaderLabels(
            ["Product", "SKU", "Category", "Qty", "Threshold"])
        self.low_stock_table.horizontalHeader().setStretchLastSection(True)
        self.low_stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.low_stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.low_stock_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.low_stock_table.setMaximumHeight(200)
        lf_layout.addWidget(self.low_stock_table)
        layout.addWidget(low_frame)

    def refresh(self):
        """Reload all dashboard data."""
        # Clear stat cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        products = db.get_all_products()
        low_stock = db.get_low_stock_products()
        sales = db.get_sales()
        total_revenue = sum(s[4] for s in sales) if sales else 0
        total_items = sum(p[6] for p in products) if products else 0

        cards = [
            ("Total Products", len(products), "#1a73e8"),
            ("Total Stock", total_items, "#0f9d58"),
            ("Low Stock Items", len(low_stock), "#db4437"),
            ("Total Revenue", f"₹{total_revenue:,.2f}", "#f4b400"),
            ("Total Sales", len(sales), "#8e24aa"),
        ]
        for title, value, color in cards:
            self.cards_layout.addWidget(StatCard(title, value, color))

        # Sales chart
        self.sales_chart.axes.clear()
        summary = db.get_sales_summary()
        if summary:
            days = [row[0][5:] for row in summary]  # MM-DD
            revenues = [row[1] for row in summary]
            self.sales_chart.axes.fill_between(range(len(days)), revenues,
                                                alpha=0.3, color='#1a73e8')
            self.sales_chart.axes.plot(range(len(days)), revenues,
                                       color='#1a73e8', linewidth=2)
            self.sales_chart.axes.set_xticks(range(len(days)))
            self.sales_chart.axes.set_xticklabels(days, rotation=45, fontsize=7)
            self.sales_chart.axes.set_ylabel("Revenue (₹)")
        else:
            self.sales_chart.axes.text(0.5, 0.5, "No sales data yet",
                                        ha='center', va='center', fontsize=12,
                                        color='#9aa0a6')
        self.sales_chart.axes.set_facecolor('#fafafa')
        self.sales_chart.fig.tight_layout()
        self.sales_chart.draw()

        # Category pie
        self.cat_chart.axes.clear()
        cat_data = db.get_category_sales()
        if cat_data:
            labels = [r[0] or "Uncategorized" for r in cat_data]
            values = [r[1] for r in cat_data]
            colors = ['#1a73e8', '#0f9d58', '#f4b400', '#db4437',
                      '#8e24aa', '#00bcd4', '#ff7043']
            self.cat_chart.axes.pie(values, labels=labels, autopct='%1.1f%%',
                                    colors=colors[:len(labels)], startangle=90,
                                    textprops={'fontsize': 8})
        else:
            self.cat_chart.axes.text(0.5, 0.5, "No data",
                                      ha='center', va='center', fontsize=12,
                                      color='#9aa0a6')
        self.cat_chart.fig.tight_layout()
        self.cat_chart.draw()

        # Low stock table
        self.low_stock_table.setRowCount(0)
        for row_data in low_stock:
            row = self.low_stock_table.rowCount()
            self.low_stock_table.insertRow(row)
            # id, name, sku, cat_name, price, cost, qty, threshold
            items = [row_data[1], row_data[2], row_data[3] or "N/A",
                     str(row_data[6]), str(row_data[7])]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                if col == 3:  # quantity column
                    item.setForeground(Qt.red)
                item.setTextAlignment(Qt.AlignCenter)
                self.low_stock_table.setItem(row, col, item)
