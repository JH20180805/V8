"""
Excel导入导出处理
"""
import pandas as pd
from database.db_manager import DatabaseManager # For type hinting if needed, though not strictly necessary for runtime

class ExcelHandler:
    """Excel处理器类"""

    def __init__(self, db_manager: DatabaseManager):
        """初始化Excel处理器

        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager

    def handler(self, file_path: str):
        """
        处理Excel导入（从指定文件路径读取并存入数据库）
        Args:
            file_path (str): 要导入的Excel文件的路径.
        """
        try:
            df = pd.read_excel(file_path)
            # For to_sql, pandas usually works well with a SQLAlchemy-like connection string
            # or a sqlite3.Connection object.
            # QSqlDatabase.databaseName() gives the file path for SQLite.
            db_name = self.db_manager.db.databaseName()
            if not self.db_manager.db.isOpen(): # Ensure connection is open
                print("ExcelHandler (import): Database connection was closed. Opening...")
                if not self.db_manager.db.open():
                    print(f"ExcelHandler (import): Failed to open database: {self.db_manager.db.lastError().text()}")
                    return False # Indicate failure

            # Using the database name (file path) for pandas to_sql with SQLite
            df.to_sql(name="tools", con=f"sqlite:///{db_name}", if_exists='replace', index=False)
            print(f"ExcelHandler (import): Data from '{file_path}' successfully imported to 'tools' table.")
            return True
        except FileNotFoundError:
            print(f"ExcelHandler (import): Error - File not found at '{file_path}'.")
            # Consider raising or returning specific error codes/messages
            return False
        except Exception as e:
            print(f"ExcelHandler (import): An error occurred during Excel import: {e}")
            return False

    def export_to_excel(self, table_name: str, file_path_to_save: str) -> bool:
        """
        从数据库的指定表导出数据到Excel文件.

        Args:
            table_name (str): 要导出数据的数据库表名.
            file_path_to_save (str): Excel文件的保存路径.

        Returns:
            bool: 成功返回 True, 失败返回 False.
        """
        try:
            db_name = self.db_manager.db.databaseName()
            if not self.db_manager.db.isOpen(): # Ensure connection is open
                print("ExcelHandler (export): Database connection was closed. Opening...")
                if not self.db_manager.db.open():
                    print(f"ExcelHandler (export): Failed to open database: {self.db_manager.db.lastError().text()}")
                    return False

            # Read data from SQLite table into pandas DataFrame
            # pd.read_sql_table requires a SQLAlchemy connectable.
            # We can construct one from the database name.
            from sqlalchemy import create_engine
            engine = create_engine(f"sqlite:///{db_name}")

            df = pd.read_sql_table(table_name, engine)

            # Save DataFrame to Excel
            df.to_excel(file_path_to_save, index=False)
            print(f"ExcelHandler (export): Data from table '{table_name}' successfully exported to '{file_path_to_save}'.")
            return True
        except FileNotFoundError: # This might occur if the directory for file_path_to_save doesn't exist
            print(f"ExcelHandler (export): Error - Directory for '{file_path_to_save}' not found or invalid path.")
            return False
        except PermissionError:
            print(f"ExcelHandler (export): Error - No write permission for '{file_path_to_save}'.")
            return False
        except Exception as e: # Catch other potential errors (e.g., table not found by pandas, other pd errors)
            print(f"ExcelHandler (export): An error occurred: {e}")
            # Check if the error is due to table not existing (specific exceptions depend on SQLAlchemy/pandas versions)
            if "no such table" in str(e).lower() or "table not found" in str(e).lower() :
                 print(f"ExcelHandler (export): Error - Table '{table_name}' not found in the database.")
            return False
