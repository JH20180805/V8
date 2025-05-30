from PySide6.QtWidgets import (QWidget, QGridLayout, QPushButton, QLabel, QSizePolicy, 
                             QFileDialog, QComboBox, QLineEdit, QTableView, QHeaderView,
                             QProgressDialog, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtGui import QFont
from database.db_manager import DatabaseManager 
from utils.report_generator import ReportGenerator
from PySide6.QtSql import QSqlQuery
import pandas as pd
import numpy as np

class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter  # 文字居中对齐
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(self._data.index[section])
        return None


class ReportTab(QWidget):
    def __init__(self, DatabaseManager):
        super().__init__()

        self.databasemanger = DatabaseManager
        df = pd.read_sql("SELECT * FROM tools", self.databasemanger.conn)

        # 筛选相同单位日期的相同样品作为1个试验批次，用来生成报告
        grouped_object = df.groupby(['委托单位', '样品名称', '接收日期'])
        dic = {}
        for name, group in grouped_object:
            dic[name] = group

        # 美化标签和下拉框
        label = QLabel("选择试验批次：")
        label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        label.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #dee2e6;
            }
        """)
        
        selec = QComboBox()
        selec.setFont(QFont("Microsoft YaHei", 10))
        selec.setStyleSheet("""
            QComboBox {
                padding: 8px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                min-width: 300px;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
            QComboBox:focus {
                border-color: #4CAF50;
                outline: none;
            }
        """)
        view = QTableView()
        for key, _ in dic.items():
            selec.addItem(str(key), key)  # 第二个参数存储原始的元组键

        # 统一的数据更新方法
        def update_current_data():
            """更新当前选中的键值对"""
            current_key = selec.currentData()
            if current_key and current_key in dic:
                self.key = current_key
                self.value = dic[current_key]
                return True
            return False
        
        # 连接ComboBox选择变化信号
        def update_table():
            if update_current_data():
                model = PandasModel(self.value)
                view.setModel(model)

        selec.currentTextChanged.connect(update_table)
        
        # 初始化时设置第一个选项的模型
        if dic:  # 确保字典不为空
            update_current_data()  # 初始化键值对
            initial_model = PandasModel(self.value)
            view.setModel(initial_model)


        # 设置表格视图的大小策略，让它能够扩展
        view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 美化表格
        view.setAlternatingRowColors(True)  # 交替行颜色
        view.setSelectionBehavior(QTableView.SelectRows)  # 选择整行
        view.setGridStyle(Qt.SolidLine)  # 网格线样式
        view.setFont(QFont("Microsoft YaHei", 9))  # 设置字体
        
        # 自适应列宽 - 根据内容调整
        header = view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # 根据内容调整列宽
        header.setStretchLastSection(True)  # 最后一列拉伸填充剩余空间
        
        # 设置行高并隐藏序号
        view.verticalHeader().setDefaultSectionSize(30)
        view.verticalHeader().setVisible(False)  # 隐藏行序号
        
        layout = QGridLayout()
        
        button = QPushButton("打印")
        button.clicked.connect(self.generate)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setMaximumWidth(80)  # 限制按钮宽度
        button.setMaximumHeight(45)  # 限制按钮高度
        button.setStyleSheet("""
            QPushButton {
                border: 2px solid #4CAF50;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)  # 设置边框样式凸显

        # 添加批量生成按钮
        batch_button = QPushButton("批量生成所有报告")
        batch_button.clicked.connect(self.generate_all_batches)
        batch_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        batch_button.setMaximumWidth(150)  # 限制按钮宽度
        batch_button.setMaximumHeight(45)  # 限制按钮高度
        batch_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #007BFF;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 4px 8px;
                background-color: #FFFFFF;
                color: #007BFF;
            }
            QPushButton:hover {
                background-color: #E7F3FF;
                border-color: #0056B3;
            }
            QPushButton:pressed {
                background-color: #CCE7FF;
            }
        """)  # 蓝色主题样式

        # 存储字典供批量生成使用
        self.dic = dic

        layout.addWidget(label, 0, 0)
        layout.addWidget(selec, 0, 1, 1, 2)  # 下拉框占2列，显示更多内容
        layout.addWidget(view, 1, 0, 1, 3)  # 表格占据3列
        layout.addWidget(button, 2, 0, 1, 1, alignment=Qt.AlignRight)
        layout.addWidget(batch_button, 2, 1, 1, 2, alignment=Qt.AlignLeft)
        
        # 设置间距和拉伸比例
        layout.setVerticalSpacing(15)  # 增加垂直间距
        layout.setHorizontalSpacing(10)  # 水平间距
        layout.setContentsMargins(15, 15, 15, 15)  # 设置边距
        layout.setRowStretch(1, 1)  # 第1行（表格）拉伸比例为1
        layout.setColumnStretch(0, 0)  # 标签列不拉伸
        layout.setColumnStretch(1, 1)  # 下拉框列拉伸
        layout.setColumnStretch(2, 1)  # 第三列拉伸

        self.setLayout(layout)

    def generate(self):
        self.generator = ReportGenerator(self.key, self.value)
        self.generator.generate_report()

    def generate_all_batches(self):
        """批量生成所有批次的报告"""
        if not hasattr(self, 'dic') or not self.dic:
            QMessageBox.warning(self, "警告", "没有可生成的批次数据")
            return
        
        total_count = len(self.dic)
        success_count = 0
        error_count = 0
        error_messages = []
        
        # 创建进度对话框
        progress = QProgressDialog("正在生成报告...", "取消", 0, total_count, self)
        progress.setWindowTitle("批量生成报告")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)  # 立即显示进度条
        progress.resize(400, 120)
        
        # 设置进度条样式
        progress.setStyleSheet("""
            QProgressDialog {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QProgressBar {
                border: 1px solid #007BFF;
                border-radius: 4px;
                text-align: center;
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                background-color: #007BFF;
                border-radius: 3px;
            }
        """)
        
        current_step = 0
        was_canceled = False
        
        for key, value in self.dic.items():
            # 检查是否取消
            if progress.wasCanceled():
                was_canceled = True
                break
                
            # 更新进度
            current_step += 1
            batch_name = f"{key[0]}_{key[1]}_{key[2]}"
            progress.setLabelText(f"正在生成第 {current_step}/{total_count} 个报告：\n{batch_name}")
            progress.setValue(current_step)
            
            try:
                generator = ReportGenerator(key, value)
                generator.generate_report()
                success_count += 1
                print(f"✓ 成功生成: {batch_name}")
            except Exception as e:
                error_count += 1
                error_msg = f"{batch_name}: {str(e)}"
                error_messages.append(error_msg)
                print(f"✗ 生成失败: {error_msg}")
        
        progress.close()
        
        # 显示结果对话框
        self.show_batch_result(success_count, error_count, error_messages, was_canceled)

    def show_batch_result(self, success_count, error_count, error_messages, was_canceled):
        """显示批量生成结果对话框"""
        if was_canceled:
            title = "操作已取消"
            message = f"批量生成已取消！\n已成功生成: {success_count} 个报告"
            icon = QMessageBox.Information
        elif error_count == 0:
            title = "生成完成"
            message = f"🎉 批量生成成功完成！\n共生成 {success_count} 个报告"
            icon = QMessageBox.Information
        else:
            title = "生成完成（部分失败）"
            message = f"批量生成完成！\n✓ 成功: {success_count} 个\n✗ 失败: {error_count} 个"
            if error_messages:
                message += f"\n\n失败详情:\n" + "\n".join(error_messages[:5])  # 只显示前5个错误
                if len(error_messages) > 5:
                    message += f"\n... 还有 {len(error_messages) - 5} 个错误"
            icon = QMessageBox.Warning
        
        msg_box = QMessageBox(icon, title, message, QMessageBox.Ok, self)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                font-family: 'Microsoft YaHei';
            }
            QMessageBox QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0056B3;
            }
        """)
        msg_box.exec()