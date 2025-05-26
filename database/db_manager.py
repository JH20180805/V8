from PySide6.QtWidgets import QApplication, QMainWindow, QTableView
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtCore import Qt
import sys
import sqlite3


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("my_database.db")
        
        # 假设数据库连接已经成功建立
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("my_database.db")
        if not self.db.open():
            print("无法连接到数据库！")
            sys.exit(1)

