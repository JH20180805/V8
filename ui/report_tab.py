from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QSizePolicy, QFileDialog, QComboBox, QLineEdit, QTableView
from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtGui import QFont
from database.db_manager import DatabaseManager 
from utils.report_generator import ReportGenerator
from PySide6.QtSql import QSqlQuery
import pandas as pd
import numpy as np

class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(self._data.index[section])
        return None


class ReportTab(QWidget):
    def __init__(self, DatabaseManager):
        super().__init__()

        self.databasemanger = DatabaseManager
        df = pd.read_sql("SELECT * FROM tools", self.databasemanger.conn)

        # 筛选相同单位日期的相同样品作为1个试验批次，用来生成报告
        grouped_object = df.groupby(['委托单位', '样品名称', '接收日期'])
        dic = {}
        for name, group in grouped_object:
            dic[name] = group

        label = QLabel("试验批次：")
        selec = QComboBox()
        view = QTableView()
        for key, _ in dic.items():
            selec.addItem(str(key), key)  # 第二个参数存储原始的元组键

        # 连接ComboBox选择变化信号
        def update_table():
            current_key = selec.currentData()
            if current_key and current_key in dic:
                model = PandasModel(dic[current_key])
                view.setModel(model)
                self.key = selec.currentData()
                self.value = dic[self.key]

        selec.currentTextChanged.connect(update_table)
        # self.key = selec.currentData()
        # self.value = dic[self.key]

        # 初始化时设置第一个选项的模型
        if dic:  # 确保字典不为空
            first_key = list(dic.keys())[0]
            initial_model = PandasModel(dic[first_key])
            view.setModel(initial_model)


        # 设置表格视图的大小策略，让它能够扩展
        view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QGridLayout()
        
        button = QPushButton("打印")
        button.clicked.connect(self.generate)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setMaximumWidth(100)  # 限制按钮宽度

        layout.addWidget(label, 0, 0)
        layout.addWidget(selec, 0, 1)
        layout.addWidget(view, 1, 0, 1, 2)  # 表格占据大部分空间
        layout.addWidget(button, 2, 0, 1, 2, alignment=Qt.AlignCenter)
        
        # 设置行列拉伸比例，让表格行占用更多空间
        layout.setRowStretch(1, 1)  # 第1行（表格）拉伸比例为1
        layout.setColumnStretch(0, 1)  # 列拉伸
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)

    def generate(self):
        self.generator = ReportGenerator(self.key, self.value)
        self.generator.generate_report()