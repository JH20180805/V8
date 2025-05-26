from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QSizePolicy, QFileDialog, QComboBox, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.db_manager import DatabaseManager 


class ReportTab(QWidget):
    def __init__(self, DatabaseManager):
        super().__init__()
        layout = QGridLayout()
        # layout.setAlignment(Qt.AlignCenter) # 整体居中
        l1 = QLabel("委托单位")
        t1 = QLineEdit()
        l2 = QLabel("样品名称")
        t2 = QLineEdit()
        l3 = QLabel("接收时间")
        t3 = QLineEdit()
        
        layout.addWidget(l1, 0, 0)
        layout.addWidget(t1, 0, 1)
        layout.addWidget(l2, 1, 0)
        layout.addWidget(t2, 1, 1)
        layout.addWidget(l3, 2, 0)
        layout.addWidget(t3, 2, 1)

        self.setLayout(layout)