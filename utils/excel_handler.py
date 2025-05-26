"""
Excel导入导出处理
"""
import pandas as pd


class ExcelHandler:
    """Excel处理器类"""

    def __init__(self, file_path, con):
        """初始化Excel处理器

        Args:
            db_manager: 数据库管理器
        """
        self.file_path = file_path
        self.conn = con

    def handler(self):
        df = pd.read_excel(self.file_path)
        df.to_sql(name="tools", con=self.conn,if_exists='replace', index=False)
