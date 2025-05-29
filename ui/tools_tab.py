from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableView, QPushButton, QLabel, QSizePolicy, QFileDialog, QHeaderView, QStyledItemDelegate
from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtGui import QFont, QIcon, QGuiApplication # 导入QGuiApplication用于获取屏幕信息
from utils.excel_handler import ExcelHandler
from database.db_manager import DatabaseManager


class CenterAlignDelegate(QStyledItemDelegate):
    """文字居中对齐委托"""
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter


class ToolTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

        if not self.db_manager.db.isOpen():
            print("数据库连接未打开，请检查 DatabaseManager 初始化。")
            if not self.db_manager.db.open():
                print("尝试重新打开数据库失败！")
                return

        layout = QVBoxLayout(self)

        self.model = QSqlTableModel(db=self.db_manager.db)
        self.model.setTable("tools")
        self.model.select()

        if self.model.lastError().isValid():
            print(f"模型错误: {self.model.lastError().text()}")
        elif self.model.rowCount() == 0:
            print("模型加载成功，但 'tools' 表中没有数据。")

        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setSortingEnabled(True)
        
        # 美化表格
        self.table_view.setAlternatingRowColors(True)  # 交替行颜色
        self.table_view.setSelectionBehavior(QTableView.SelectRows)  # 选择整行
        self.table_view.setGridStyle(Qt.SolidLine)  # 网格线样式
        self.table_view.setFont(QFont("Microsoft YaHei", 9))  # 设置字体
        
        # 自适应列宽 - 根据内容调整
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # 根据内容调整列宽
        header.setStretchLastSection(True)  # 最后一列拉伸填充剩余空间
        
        # 设置行高
        self.table_view.verticalHeader().setDefaultSectionSize(30)
        
        # 设置文字居中对齐
        center_delegate = CenterAlignDelegate()
        self.table_view.setItemDelegate(center_delegate)

        layout.addWidget(self.table_view)


