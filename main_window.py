"""
main_window.py - Main application window with sidebar navigation.
"""

import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from dashboard import DashboardPage
from products_page import ProductsPage
from stock_page import StockPage
from sales_page import SalesPage
from reports_page import ReportsPage


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Inventory Management System")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---- Sidebar ----
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # App title
        app_title = QLabel("🗃️ Inventory\n    Manager")
        app_title.setObjectName("appTitle")
        sidebar_layout.addWidget(app_title)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #dadce0;")
        sidebar_layout.addWidget(sep)

        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("📊  Dashboard", 0),
            ("📦  Products", 1),
            ("🔄  Stock", 2),
            ("💰  Sales", 3),
            ("📈  Reports", 4),
        ]

        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=idx: self.navigate(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # Version label
        ver_label = QLabel("v1.0.0")
        ver_label.setAlignment(Qt.AlignCenter)
        ver_label.setStyleSheet("color: #9aa0a6; font-size: 11px; padding: 12px;")
        sidebar_layout.addWidget(ver_label)

        main_layout.addWidget(sidebar)

        # ---- Content area ----
        self.stack = QStackedWidget()

        self.dashboard_page = DashboardPage()
        self.products_page = ProductsPage()
        self.stock_page = StockPage()
        self.sales_page = SalesPage()
        self.reports_page = ReportsPage()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.products_page)
        self.stack.addWidget(self.stock_page)
        self.stack.addWidget(self.sales_page)
        self.stack.addWidget(self.reports_page)

        main_layout.addWidget(self.stack, stretch=1)

        # Default to Dashboard
        self.navigate(0)

    def navigate(self, index):
        """Switch to the page at `index` and refresh its data."""
        self.stack.setCurrentIndex(index)

        # Update button styles
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Refresh current page
        page = self.stack.currentWidget()
        if hasattr(page, 'refresh'):
            page.refresh()
