import sys
from PySide6.QtWidgets import (QApplication, QTabWidget, QWidget, QVBoxLayout, 
                               QPushButton, QLabel, QSizePolicy, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QGuiApplication # 导入QGuiApplication用于获取屏幕信息
from utils.excel_handler import ExcelHandler
from database.db_manager import DatabaseManager
from .tools_tab import ToolTab
from .quick_start_tab import QuickStart
from .report_tab import ReportTab

class MainWindow(QWidget):
    def __init__(self):
        print("MainWindow.__init__: Starting.")
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

        self.db_manager = DatabaseManager() # 创建 DatabaseManager 实例
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

    def switch_tab(self, tab_name):
    # """切换到指定名称的选项卡"""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == tab_name:
                self.tab_widget.setCurrentIndex(i)
                return True
        return False

    def setup_ui(self):
        layout = QVBoxLayout(self)

        print("MainWindow.setup_ui: Creating QTabWidget...")
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Microsoft YaHei", 10))
        print("MainWindow.setup_ui: QTabWidget created.")

        print("MainWindow.setup_ui: Creating QuickStart tab...")
        self.quick_tab = QuickStart(ExcelHandler, self.db_manager, self)
        print("MainWindow.setup_ui: QuickStart tab created.")

        print("MainWindow.setup_ui: Creating ToolTab...")
        self.tool_tab = ToolTab(self.db_manager)
        print("MainWindow.setup_ui: ToolTab created.")

        print("MainWindow.setup_ui: Creating ReportTab...")
        self.report_tab = ReportTab(self.db_manager)
        print("MainWindow.setup_ui: ReportTab created.")

        print("MainWindow.setup_ui: Adding tabs to QTabWidget...")
        self.tab_widget.addTab(self.quick_tab, "快速开始")
        self.tab_widget.addTab(self.tool_tab, "数据预览")
        self.tab_widget.addTab(self.report_tab, "报告打印")
        print("MainWindow.setup_ui: Tabs added.")

        layout.addWidget(self.tab_widget)
        print("MainWindow.setup_ui: QTabWidget added to layout.")

        # 设置全局样式
        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA; /* Neutral Light Background */
            }
            QTabWidget::pane {
                border: 1px solid #DEE2E6;
                border-radius: 4px;
                background-color: #FFFFFF;
                margin-top: 10px; /* tab与内容区域间距 */
            }
            QTabBar::tab {
                background-color: #E9ECEF;
                border: 1px solid #DEE2E6;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                color: #6C757D;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                border-color: #007BFF;
                color: #007BFF;
                font-weight: 600;
                border-bottom: 2px solid #FFFFFF; /* 连接到内容区域 */
            }
            QTabBar::tab:hover:!selected {
                background-color: #F8F9FA;
                color: #495057;
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
                # 连接信号和槽
        self.tab_widget.currentChanged.connect(self.on_tab_changed)


    def on_tab_changed(self, index):
        """选项卡切换事件处理

        Args:
            index: 选项卡索引
        """
        # 刷新当前选项卡的数据
        current_tab_widget = self.tab_widget.widget(index)
        tab_name = self.tab_widget.tabText(index)
        print(f"MainWindow: Tab changed to '{tab_name}' (index {index}). Checking for refresh_data.")
        if hasattr(current_tab_widget, 'refresh_data') and callable(current_tab_widget.refresh_data):
            print(f"MainWindow: Calling refresh_data() on tab '{tab_name}'.")
            current_tab_widget.refresh_data()
            print(f"MainWindow: Finished calling refresh_data() on tab '{tab_name}'.")
        else:
            print(f"MainWindow: Tab '{tab_name}' does not have a callable refresh_data method.")



