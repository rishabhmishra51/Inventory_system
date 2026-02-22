"""
reports_page.py - Reports & Charts page with Matplotlib visualizations and CSV export.
"""

import os
from datetime import datetime

import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import database as db


class ChartCanvas(FigureCanvas):
    """Reusable Matplotlib canvas."""

    def __init__(self, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#ffffff')
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class ReportsPage(QWidget):
    """Reports page with charts and CSV export."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("📊  Reports & Analytics")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        export_products_btn = QPushButton("📄  Export Products CSV")
        export_products_btn.setObjectName("outlineBtn")
        export_products_btn.clicked.connect(self.export_products_csv)
        header.addWidget(export_products_btn)

        export_sales_btn = QPushButton("📄  Export Sales CSV")
        export_sales_btn.setObjectName("outlineBtn")
        export_sales_btn.clicked.connect(self.export_sales_csv)
        header.addWidget(export_sales_btn)

        export_stock_btn = QPushButton("📄  Export Stock CSV")
        export_stock_btn.setObjectName("primaryBtn")
        export_stock_btn.clicked.connect(self.export_stock_csv)
        header.addWidget(export_stock_btn)

        layout.addLayout(header)

        # Tabs
        tabs = QTabWidget()

        # ---- Sales Trend chart ----
        sales_tab = QWidget()
        sl = QVBoxLayout(sales_tab)
        sl.setContentsMargins(12, 12, 12, 12)
        self.sales_canvas = ChartCanvas(8, 4)
        sl.addWidget(self.sales_canvas)
        tabs.addTab(sales_tab, "📈  Sales Trend")

        # ---- Top Products chart ----
        top_tab = QWidget()
        tl = QVBoxLayout(top_tab)
        tl.setContentsMargins(12, 12, 12, 12)
        self.top_canvas = ChartCanvas(8, 4)
        tl.addWidget(self.top_canvas)
        tabs.addTab(top_tab, "🏆  Top Products")

        # ---- Category Revenue pie ----
        cat_tab = QWidget()
        cl = QVBoxLayout(cat_tab)
        cl.setContentsMargins(12, 12, 12, 12)
        self.cat_canvas = ChartCanvas(6, 5)
        cl.addWidget(self.cat_canvas)
        tabs.addTab(cat_tab, "🏷️  Category Revenue")

        # ---- Stock Overview bar chart ----
        stock_tab = QWidget()
        stl = QVBoxLayout(stock_tab)
        stl.setContentsMargins(12, 12, 12, 12)
        self.stock_canvas = ChartCanvas(8, 4)
        stl.addWidget(self.stock_canvas)
        tabs.addTab(stock_tab, "📦  Stock Overview")

        # ---- Profit Analysis ----
        profit_tab = QWidget()
        pl = QVBoxLayout(profit_tab)
        pl.setContentsMargins(12, 12, 12, 12)
        self.profit_canvas = ChartCanvas(8, 4)
        pl.addWidget(self.profit_canvas)
        tabs.addTab(profit_tab, "💹  Profit Analysis")

        layout.addWidget(tabs)

    def refresh(self):
        self._draw_sales_trend()
        self._draw_top_products()
        self._draw_category_pie()
        self._draw_stock_overview()
        self._draw_profit_analysis()

    # ---- Chart renderers ----

    def _draw_sales_trend(self):
        self.sales_canvas.fig.clear()
        ax = self.sales_canvas.fig.add_subplot(111)
        ax.set_facecolor('#fafafa')

        data = db.get_sales_summary()
        if data:
            days = [r[0] for r in data]
            revenue = [r[1] for r in data]
            units = [r[2] for r in data]

            ax.bar(range(len(days)), revenue, color='#1a73e8', alpha=0.7, label='Revenue (₹)')
            ax2 = ax.twinx()
            ax2.plot(range(len(days)), units, color='#db4437', linewidth=2,
                     marker='o', markersize=4, label='Units Sold')
            ax2.set_ylabel("Units Sold", color='#db4437')

            ax.set_xticks(range(len(days)))
            ax.set_xticklabels([d[5:] for d in days], rotation=45, fontsize=8)
            ax.set_ylabel("Revenue (₹)")
            ax.set_title("Daily Sales Trend (Last 30 Days)", fontweight='bold', fontsize=12)
            ax.legend(loc='upper left', fontsize=8)
            ax2.legend(loc='upper right', fontsize=8)
        else:
            ax.text(0.5, 0.5, "No sales data available", ha='center', va='center',
                    fontsize=14, color='#9aa0a6')
            ax.set_title("Daily Sales Trend", fontweight='bold')

        self.sales_canvas.fig.tight_layout()
        self.sales_canvas.draw()

    def _draw_top_products(self):
        self.top_canvas.fig.clear()
        ax = self.top_canvas.fig.add_subplot(111)
        ax.set_facecolor('#fafafa')

        data = db.get_top_products(10)
        if data:
            names = [r[0][:20] for r in data]
            revenue = [r[2] for r in data]
            colors = ['#1a73e8', '#0f9d58', '#f4b400', '#db4437', '#8e24aa',
                      '#00bcd4', '#ff7043', '#795548', '#607d8b', '#e91e63']
            ax.barh(range(len(names)), revenue, color=colors[:len(names)])
            ax.set_yticks(range(len(names)))
            ax.set_yticklabels(names, fontsize=9)
            ax.set_xlabel("Revenue (₹)")
            ax.set_title("Top 10 Products by Revenue", fontweight='bold', fontsize=12)
            ax.invert_yaxis()
            for i, v in enumerate(revenue):
                ax.text(v + max(revenue) * 0.01, i, f"₹{v:,.0f}", va='center', fontsize=8)
        else:
            ax.text(0.5, 0.5, "No sales data available", ha='center', va='center',
                    fontsize=14, color='#9aa0a6')
            ax.set_title("Top Products", fontweight='bold')

        self.top_canvas.fig.tight_layout()
        self.top_canvas.draw()

    def _draw_category_pie(self):
        self.cat_canvas.fig.clear()
        ax = self.cat_canvas.fig.add_subplot(111)

        data = db.get_category_sales()
        if data:
            labels = [r[0] or "Uncategorized" for r in data]
            values = [r[1] for r in data]
            colors = ['#1a73e8', '#0f9d58', '#f4b400', '#db4437',
                      '#8e24aa', '#00bcd4', '#ff7043']
            wedges, texts, autotexts = ax.pie(
                values, labels=labels, autopct='%1.1f%%',
                colors=colors[:len(labels)], startangle=90,
                textprops={'fontsize': 9}
            )
            for t in autotexts:
                t.set_fontsize(8)
                t.set_fontweight('bold')
            ax.set_title("Revenue by Category", fontweight='bold', fontsize=12)
        else:
            ax.text(0.5, 0.5, "No data available", ha='center', va='center',
                    fontsize=14, color='#9aa0a6')
            ax.set_title("Category Revenue", fontweight='bold')

        self.cat_canvas.fig.tight_layout()
        self.cat_canvas.draw()

    def _draw_stock_overview(self):
        self.stock_canvas.fig.clear()
        ax = self.stock_canvas.fig.add_subplot(111)
        ax.set_facecolor('#fafafa')

        products = db.get_all_products()
        if products:
            names = [p[1][:18] for p in products[:20]]  # limit for readability
            qtys = [p[6] for p in products[:20]]
            thresholds = [p[7] for p in products[:20]]

            x = range(len(names))
            bar_colors = ['#db4437' if q <= t else '#0f9d58' for q, t in zip(qtys, thresholds)]
            ax.bar(x, qtys, color=bar_colors, alpha=0.8, label='Current Stock')
            ax.plot(x, thresholds, color='#f4b400', linewidth=2,
                    linestyle='--', marker='s', markersize=4, label='Threshold')
            ax.set_xticks(x)
            ax.set_xticklabels(names, rotation=45, fontsize=8, ha='right')
            ax.set_ylabel("Quantity")
            ax.set_title("Stock Levels vs Thresholds", fontweight='bold', fontsize=12)
            ax.legend(fontsize=9)
        else:
            ax.text(0.5, 0.5, "No products available", ha='center', va='center',
                    fontsize=14, color='#9aa0a6')
            ax.set_title("Stock Overview", fontweight='bold')

        self.stock_canvas.fig.tight_layout()
        self.stock_canvas.draw()

    def _draw_profit_analysis(self):
        self.profit_canvas.fig.clear()
        ax = self.profit_canvas.fig.add_subplot(111)
        ax.set_facecolor('#fafafa')

        # Calculate per-product profit from sales
        conn = db.get_connection()
        rows = conn.execute("""
            SELECT p.name, 
                   SUM(s.total) as revenue,
                   SUM(s.quantity_sold * p.cost_price) as cost,
                   SUM(s.total) - SUM(s.quantity_sold * p.cost_price) as profit
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.name
            ORDER BY profit DESC
            LIMIT 10
        """).fetchall()
        conn.close()

        if rows:
            names = [r[0][:18] for r in rows]
            revenue = [r[1] for r in rows]
            cost = [r[2] for r in rows]
            profit = [r[3] for r in rows]

            x = range(len(names))
            width = 0.3
            ax.bar([i - width for i in x], revenue, width, color='#1a73e8',
                   alpha=0.8, label='Revenue')
            ax.bar(x, cost, width, color='#db4437', alpha=0.8, label='Cost')
            ax.bar([i + width for i in x], profit, width, color='#0f9d58',
                   alpha=0.8, label='Profit')

            ax.set_xticks(x)
            ax.set_xticklabels(names, rotation=45, fontsize=8, ha='right')
            ax.set_ylabel("Amount (₹)")
            ax.set_title("Profit Analysis — Top 10 Products", fontweight='bold', fontsize=12)
            ax.legend(fontsize=9)
        else:
            ax.text(0.5, 0.5, "No sales data available", ha='center', va='center',
                    fontsize=14, color='#9aa0a6')
            ax.set_title("Profit Analysis", fontweight='bold')

        self.profit_canvas.fig.tight_layout()
        self.profit_canvas.draw()

    # ---- CSV Exports ----

    def export_products_csv(self):
        products = db.get_all_products()
        if not products:
            QMessageBox.information(self, "No Data", "No products to export.")
            return
        df = pd.DataFrame(products, columns=[
            "ID", "Name", "SKU", "Category", "Price", "Cost Price",
            "Quantity", "Low Stock Threshold", "Description",
            "Created At", "Updated At", "Category ID"
        ])
        df = df.drop(columns=["Category ID"])
        self._save_csv(df, "products")

    def export_sales_csv(self):
        sales = db.get_sales()
        if not sales:
            QMessageBox.information(self, "No Data", "No sales to export.")
            return
        df = pd.DataFrame(sales, columns=[
            "ID", "Product", "Qty Sold", "Sale Price", "Total", "Sale Date"
        ])
        self._save_csv(df, "sales")

    def export_stock_csv(self):
        movements = db.get_stock_movements()
        if not movements:
            QMessageBox.information(self, "No Data", "No stock movements to export.")
            return
        df = pd.DataFrame(movements, columns=[
            "ID", "Product", "Type", "Quantity", "Note", "Date"
        ])
        self._save_csv(df, "stock_movements")

    def _save_csv(self, df, prefix):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{prefix}_{timestamp}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", default_name, "CSV Files (*.csv)"
        )
        if path:
            df.to_csv(path, index=False)
            QMessageBox.information(self, "Exported ✅",
                                    f"Data exported successfully to:\n{path}")
