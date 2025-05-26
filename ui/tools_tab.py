from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableView, QPushButton, QLabel, QSizePolicy, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtGui import QFont, QIcon, QGuiApplication # 导入QGuiApplication用于获取屏幕信息
from utils.excel_handler import ExcelHandler
from database.db_manager import DatabaseManager


class ToolTab(QWidget):
    def __init__(self):
        super().__init__()
                # 创建 QSqlTableModel
        self.model = QSqlTableModel()
        self.model.setTable("tools") # 设置要显示的表格名称
        self.model.select() # 从数据库中获取数据

        # 创建 QTableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model) # 将模型设置给 QTableView

        # 允许排序（回答你刚才的思考题）
        self.table_view.setSortingEnabled(True)


        # self.setCentralWidget(self.table_view)

