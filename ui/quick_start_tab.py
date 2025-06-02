from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox # Added for QMessageBox

class QuickStart(QWidget):
    def __init__(self, excel_handler_class, db_manager_instance, main_window_instance): # Modified signature
        super().__init__()
        self.excel_handler_class = excel_handler_class # Store the class type
        self.db_manager = db_manager_instance     # Store the DatabaseManager instance
        self.main_window = main_window_instance     # Store the MainWindow instance
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
    
    # Removed get_main_window method as self.main_window is now directly available.

    def create_button(self, text, slot, layout):
        button = QPushButton(text)
        button.clicked.connect(slot)
        # 设置按钮的尺寸策略，使其在布局中可以根据内容调整，并尝试占据可用空间
        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addWidget(button, alignment=Qt.AlignCenter) # 按钮在布局中也居中
    
    def import_excel(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog # Uncomment if native dialog causes issues
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 Excel 文件",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)",
            options=options
        )

        if file_path:
            # self.excel_handler_class was stored from __init__
            # self.db_manager was stored from __init__
            excel_handler_instance = self.excel_handler_class(self.db_manager)
            success = excel_handler_instance.handler(file_path)

            if success:
                QMessageBox.information(self, "导入成功",
                                        f"数据已成功从\n{file_path}\n导入！\n\n其他数据标签页将尝试刷新。")

                # Refresh ToolTab (Data Preview) if it exists and has refresh_data
                if hasattr(self.main_window, 'tool_tab') and \
                   hasattr(self.main_window.tool_tab, 'refresh_data') and \
                   callable(self.main_window.tool_tab.refresh_data):
                    print("QuickStart: Refreshing ToolTab...")
                    self.main_window.tool_tab.refresh_data()
                else:
                    print("QuickStart: ToolTab or its refresh_data method not found/callable on MainWindow.")

                # Refresh ReportTab if it exists and has refresh_data
                if hasattr(self.main_window, 'report_tab') and \
                   hasattr(self.main_window.report_tab, 'refresh_data') and \
                   callable(self.main_window.report_tab.refresh_data):
                    print("QuickStart: Refreshing ReportTab...")
                    self.main_window.report_tab.refresh_data()
                else:
                    print("QuickStart: ReportTab or its refresh_data method not found/callable on MainWindow.")

                # Switch to the ToolTab (Data Preview)
                if hasattr(self.main_window, 'switch_tab'):
                    self.main_window.switch_tab("数据预览")
                else:
                    print("QuickStart: switch_tab method not found on MainWindow.")

            else:
                QMessageBox.warning(self, "导入失败",
                                    f"无法从\n{file_path}\n导入数据。\n\n请检查文件格式或内容，并查看控制台日志获取详细信息。")

    def view_data(self):
        # 切换到数据预览标签页
        if hasattr(self.main_window, 'switch_tab'):
            self.main_window.switch_tab("数据预览")
        else:
            print("QuickStart: switch_tab method not found on MainWindow for view_data.")

    def generate_report(self):
        # 切换到报告生成与打印标签页
        if hasattr(self.main_window, 'switch_tab'):
            self.main_window.switch_tab("报告打印")
        else:
            print("QuickStart: switch_tab method not found on MainWindow for generate_report.")