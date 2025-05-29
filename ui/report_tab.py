from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QSizePolicy, QFileDialog, QComboBox, QLineEdit, QTableView, QHeaderView
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
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter  # 文字居中对齐
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

        # 美化标签和下拉框
        label = QLabel("选择试验批次：")
        label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        label.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #dee2e6;
            }
        """)
        
        selec = QComboBox()
        selec.setFont(QFont("Microsoft YaHei", 10))
        selec.setStyleSheet("""
            QComboBox {
                padding: 8px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                min-width: 300px;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
            QComboBox:focus {
                border-color: #4CAF50;
                outline: none;
            }
        """)
        view = QTableView()
        for key, _ in dic.items():
            selec.addItem(str(key), key)  # 第二个参数存储原始的元组键

        # 统一的数据更新方法
        def update_current_data():
            """更新当前选中的键值对"""
            current_key = selec.currentData()
            if current_key and current_key in dic:
                self.key = current_key
                self.value = dic[current_key]
                return True
            return False
        
        # 连接ComboBox选择变化信号
        def update_table():
            if update_current_data():
                model = PandasModel(self.value)
                view.setModel(model)

        selec.currentTextChanged.connect(update_table)
        
        # 初始化时设置第一个选项的模型
        if dic:  # 确保字典不为空
            update_current_data()  # 初始化键值对
            initial_model = PandasModel(self.value)
            view.setModel(initial_model)


        # 设置表格视图的大小策略，让它能够扩展
        view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 美化表格
        view.setAlternatingRowColors(True)  # 交替行颜色
        view.setSelectionBehavior(QTableView.SelectRows)  # 选择整行
        view.setGridStyle(Qt.SolidLine)  # 网格线样式
        view.setFont(QFont("Microsoft YaHei", 9))  # 设置字体
        
        # 自适应列宽 - 根据内容调整
        header = view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # 根据内容调整列宽
        header.setStretchLastSection(True)  # 最后一列拉伸填充剩余空间
        
        # 设置行高并隐藏序号
        view.verticalHeader().setDefaultSectionSize(30)
        view.verticalHeader().setVisible(False)  # 隐藏行序号
        
        layout = QGridLayout()
        
        button = QPushButton("打印")
        button.clicked.connect(self.generate)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setMaximumWidth(80)  # 限制按钮宽度
        button.setMaximumHeight(45)  # 限制按钮高度
        button.setStyleSheet("""
            QPushButton {
                border: 2px solid #4CAF50;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)  # 设置边框样式凸显

        layout.addWidget(label, 0, 0)
        layout.addWidget(selec, 0, 1, 1, 2)  # 下拉框占2列，显示更多内容
        layout.addWidget(view, 1, 0, 1, 3)  # 表格占据3列
        layout.addWidget(button, 2, 0, 1, 3, alignment=Qt.AlignCenter)
        
        # 设置间距和拉伸比例
        layout.setVerticalSpacing(15)  # 增加垂直间距
        layout.setHorizontalSpacing(10)  # 水平间距
        layout.setContentsMargins(15, 15, 15, 15)  # 设置边距
        layout.setRowStretch(1, 1)  # 第1行（表格）拉伸比例为1
        layout.setColumnStretch(0, 0)  # 标签列不拉伸
        layout.setColumnStretch(1, 1)  # 下拉框列拉伸
        layout.setColumnStretch(2, 1)  # 第三列拉伸

        self.setLayout(layout)

    def generate(self):
        self.generator = ReportGenerator(self.key, self.value)
        self.generator.generate_report()