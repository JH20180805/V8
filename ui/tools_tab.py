from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableView, QPushButton, QLabel, QSizePolicy, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtGui import QFont, QIcon, QGuiApplication # 导入QGuiApplication用于获取屏幕信息
from utils.excel_handler import ExcelHandler
from database.db_manager import DatabaseManager


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

        # 允许排序（回答你刚才的思考题）
        self.table_view.setSortingEnabled(True)

        layout.addWidget(self.table_view)


        # self.setCentralWidget(self.table_view)

