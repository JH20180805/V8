from PySide6.QtWidgets import QApplication, QMainWindow, QTableView
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtCore import Qt
import sys
import sqlite3


class DatabaseManager:
    def __init__(self, widw):
        conn = sqlite3.connect("my_database.db")

        # 假设数据库连接已经成功建立
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("my_database.db")
        if not db.open():
            print("无法连接到数据库！")
            sys.exit(1)

        # 创建 QSqlTableModel
        widw.model = QSqlTableModel()
        widw.model.setTable("tools") # 设置要显示的表格名称
        widw.model.select() # 从数据库中获取数据

        # 创建 QTableView
        widw.table_view = QTableView()
        widw.table_view.setModel(self.model) # 将模型设置给 QTableView

        # 允许排序（回答你刚才的思考题）
        widw.table_view.setSortingEnabled(True)


        widw.setCentralWidget(self.table_view)
    


