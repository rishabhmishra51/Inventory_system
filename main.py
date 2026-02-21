import sys
from PyQt5.QtWidgets import QApplication
from database.db_manager import create_tables
from ui.dashboard import Dashboard

if __name__ == "__main__":
    create_tables()
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())