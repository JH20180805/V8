import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QGuiApplication # 导入QGuiApplication用于获取屏幕信息

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("工器具试验报告生成打印")

        # 设置窗口图标
        icon_path = 'icon.ico' 
        try:
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"无法加载图标: {e}. 请确保图标文件存在且路径正确。")
            # 如果图标加载失败，可以设置一个默认图标或不设置

        # 设置窗口初始大小 (可以先设置，再居中)
        self.setGeometry(100, 100, 600, 400)

        # 使窗口居中
        self.center_window()

        self.setup_ui()

    def center_window(self):
        # 获取屏幕的几何信息
        screen = QGuiApplication.primaryScreen().geometry()
        # 获取窗口的几何信息
        window = self.frameGeometry()
        # 计算窗口居中后的左上角坐标
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        # 移动窗口到计算出的位置
        self.move(x, y)

    def setup_ui(self):
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

        # 设置全局样式
        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA; /* Neutral Light Background */
            }
            QPushButton {
                background-color: #FFFFFF; /* White Card Background */
                border: 1px solid #DEE2E6; /* Light Gray Border */
                border-radius: 8px;
                padding: 20px 40px;
                font-size: 16px;
                font-weight: 600;
                color: #343A40; /* Neutral Dark Text */
                margin-bottom: 15px; /* Space between buttons */
                min-width: 250px; /* 最小宽度 */
                max-width: 350px; /* 最大宽度 */
            }
            QPushButton:hover {
                background-color: #E9ECEF; /* Slightly darker on hover */
                border-color: #007BFF; /* Primary Color Border on Hover */
            }
            QPushButton:pressed {
                background-color: #DEE2E6; /* Even darker when pressed */
            }
        """)

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
            # 导入成功后，切换到数据预览标签页
        #     # self.parent().switch_tab("数据预览") # 假设父窗口有切换标签页的方法

    def view_data(self):
        print("查看已导入数据功能被点击")
        # 实际应用中会切换到数据预览标签页
        # self.parent().switch_tab("数据预览")

    def generate_report(self):
        print("开始生成报告功能被点击")
        # 实际应用中会切换到报告生成与打印标签页
        # self.parent().switch_tab("报告生成与打印")
