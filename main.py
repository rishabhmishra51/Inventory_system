"""
Smart Inventory Management System
==================================
Entry point. Initializes the database, applies styles, and launches the PyQt5 app.
"""

import sys
import os

# Ensure the project directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

import database as db
from styles import GLOBAL_STYLE
from main_window import MainWindow


def main():
    # Initialize database tables
    db.init_db()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
