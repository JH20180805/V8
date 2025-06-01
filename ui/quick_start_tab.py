from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class QuickStart(QWidget):
    def __init__(self, ExcelHandler, DatabaseManager):
        super().__init__()
        self.ExcelHandler = ExcelHandler
        self.DatabaseManager = DatabaseManager
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter) # 整体居中

        # 欢迎信息
        welcome_label = QLabel("欢迎使用绝缘工器具试验报告打印系统！")
        welcome_label.setFont(QFont("Inter", 18, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("color: #007BFF; margin-bottom: 20px;") # Primary Color
        main_layout.addWidget(welcome_label)

        # 简要功能介绍
        intro_label = QLabel("通过以下快速入口开始您的工作：")
        intro_label.setFont(QFont("Inter", 12))
        intro_label.setAlignment(Qt.AlignCenter)
        intro_label.setStyleSheet("color: #343A40; margin-bottom: 30px;") # Neutral Dark Color
        main_layout.addWidget(intro_label)

        # 创建大按钮/卡片
        self.create_button("导入 Excel 文件", self.import_excel, main_layout)
        self.create_button("查看已导入数据", self.view_data, main_layout)
        self.create_button("开始生成报告", self.generate_report, main_layout)

        self.setLayout(main_layout)
    
    def get_main_window(self):
            """向上遍历父对象直到找到MainWindow实例"""
            parent = self.parent()
            while parent is not None:
                # 检查是否是MainWindow（通过特定属性判断）
                if hasattr(parent, 'tab_widget') and hasattr(parent, 'switch_tab'):
                    return parent
                parent = parent.parent()
            return None

    def create_button(self, text, slot, layout):
        button = QPushButton(text)
        button.clicked.connect(slot)
        # 设置按钮的尺寸策略，使其在布局中可以根据内容调整，并尝试占据可用空间
        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addWidget(button, alignment=Qt.AlignCenter) # 按钮在布局中也居中
    
    def import_excel(self):
        # 实际应用中会触发文件选择对话框
        print("导入 Excel 文件功能被点击")
        # 这里可以添加文件选择对话框的代码，例如：
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 Excel 文件", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            print(f"选择了文件: {file_path}")
            db_mag = self.DatabaseManager
            excel_hand = self.ExcelHandler(file_path, db_mag.conn)
            excel_hand.handler()
            # 使用更可靠的方式切换选项卡
            main_window = self.get_main_window()
            if main_window:
                main_window.switch_tab("数据预览")  # 确保名称完全匹配
            else:
                print("错误：无法找到主窗口")

    def view_data(self):
        # 切换到数据预览标签页
        main_window = self.get_main_window()
        if main_window:
            main_window.switch_tab("数据预览")  # 确保名称完全匹配
        else:
            print("错误：无法找到主窗口")

    def generate_report(self):
        # 切换到报告生成与打印标签页
        main_window = self.get_main_window()
        if main_window:
            main_window.switch_tab("报告打印")  # 确保名称完全匹配
        else:
            print("错误：无法找到主窗口")