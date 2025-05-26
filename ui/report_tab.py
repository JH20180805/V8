from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.db_manager import DatabaseManager 


class ReportTab(QWidget):
    super().__init__()
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignCenter) # 整体居中
