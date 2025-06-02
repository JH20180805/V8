from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtCore import Qt
import sys

class DatabaseManager:
    def __init__(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("my_database.db")
        if not self.db.open():
            print(f"错误: 无法连接到数据库！ {self.db.lastError().text()}")
            # Potentially raise an exception here instead of sys.exit
            # For now, we'll stick to printing and exiting as per original partial behavior
            sys.exit(1)

        print("数据库连接成功！")
        self.create_tools_table()

    def create_tools_table(self):
        # The 'tools' table schema is now defined by the Excel import process using pandas.to_sql,
        # which creates the table based on the DataFrame structure if it doesn't exist,
        # or replaces it if if_exists='replace' is used.
        # This method is kept for potential future use with other tables or DB setup tasks
        # that might require explicit schema definition or other setup logic.
        # For now, it only logs that the 'tools' table creation is deferred.

        # We can still check if the table exists and log that, but we won't create it here.
        query = QSqlQuery(self.db) # QSqlQuery might still be needed if we check for other tables.
        tables = self.db.tables()

        if "tools" in tables:
            print("DatabaseManager: Table 'tools' already exists. Its schema will be handled by the import process.")
        else:
            print("DatabaseManager: Table 'tools' does not currently exist. It will be created upon data import.")

        print("DatabaseManager: 'tools' table schema definition is deferred to the data import process.")

    def get_qt_connection(self):
        return self.db

    def get_connection(self):
        # This returns the name of the connection, which can be used by some libraries.
        # For a raw DBAPI2 connection, further steps might be needed if QSqlDatabase
        # doesn't directly expose it in a way pandas can use.
        # However, pandas can often work with the connection name or by passing a QSqlQuery object.
        # If a direct DBAPI2 object is strictly needed, we might need to explore
        # if Qt provides a way to get the underlying sqlite3 connection handle
        # when QSQLITE driver is used. For now, returning the database name
        # or the QSqlDatabase object itself is standard.
        # Let's assume for now that other parts of the application will adapt
        # or that pandas can use the QSqlDatabase object or its name.
        return self.db # Or self.db.connectionName() if a name is preferred.
                       # For pd.read_sql, passing the QSqlDatabase object might work with SQLAlchemy engine,
                       # or one might need to construct an SQLAlchemy engine around it.
                       # A more direct approach for pandas with Qt is often to query data into a QSqlTableModel
                       # or QSqlQueryModel and then convert that model to a pandas DataFrame.

    def close(self):
        if self.db.isOpen():
            self.db.close()
            print("数据库连接已关闭.")

# Example usage (optional, for testing purposes)
if __name__ == '__main__':
    # This requires a QApplication instance if any GUI components were involved,
    # but for pure database logic, it might run. However, Qt's SQL module
    # can sometimes be sensitive to the absence of a QApplication event loop.
    # For robust testing, especially if issues arise, running within a
    # QApplication context is advisable.

    # from PySide6.QtWidgets import QApplication
    # app = QApplication(sys.argv) # Needed for QSqlDatabase to function fully

    db_manager = DatabaseManager()

    # Test insertion (Example)
    query = QSqlQuery(db_manager.get_qt_connection())
    query.prepare("INSERT INTO tools (委托单位, 样品名称) VALUES (?, ?)")
    query.addBindValue("测试委托单位")
    query.addBindValue("测试样品")
    if query.exec():
        print("测试数据插入成功.")
    else:
        print(f"测试数据插入失败: {query.lastError().text()}")

    # Test retrieval (Example)
    query.exec("SELECT * FROM tools")
    while query.next():
        print(f"ID: {query.value('id')}, 委托单位: {query.value('委托单位')}, 样品名称: {query.value('样品名称')}")

    db_manager.close()

    # if 'app' in locals():
    #     sys.exit(app.exec())
