from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QSizePolicy, QFileDialog, QComboBox, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.db_manager import DatabaseManager 
from utils.report_generator import ReportGenerator
from PySide6.QtSql import QSqlQuery
import pandas as pd
import numpy as np


class ReportTab(QWidget):
    def __init__(self, DatabaseManager):
        super().__init__()

        self.databasemanger = DatabaseManager
        df = pd.read_sql("tools", self.databasemanger.conn)
        units = df["委托单位"].unique()
        tool_names = df["样品名称"].unique()
        receive_time = df["接收时间"].unique()


        layout = QGridLayout()
        # layout.setAlignment(Qt.AlignCenter) # 整体居中
        l1 = QLabel("委托单位")
        t1 = QComboBox()
        t1.addItems(units)
        l2 = QLabel("样品名称")
        t2 = QComboBox()
        t2.addItems(tool_names)
        l3 = QLabel("接收时间")
        t3 = QComboBox()
        t3.addItems(receive_time)
        l4 = QPushButton("打印")
        l4.clicked.connect(self.generate())

        df_new = df["委托单位"==t1.textActivated & "样品名称"==t2.textActivated & "接收时间"==t3.textActivated]
        print(df_new)
        
        layout.addWidget(l1, 0, 0)
        layout.addWidget(t1, 0, 1)
        layout.addWidget(l2, 1, 0)
        layout.addWidget(t2, 1, 1)
        layout.addWidget(l3, 2, 0)
        layout.addWidget(t3, 2, 1)
        layout.addWidget(l4, 3, 0, 1, 2)

        self.setLayout(layout)

    def generate(self):
        self.generator = ReportGenerator()
        self.generator.generate_report()