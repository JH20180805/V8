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
    def __init__(self, database_manager: DatabaseManager): # Corrected type hint
        super().__init__()

        self.db_manager = database_manager # Corrected variable name
        self.dic = {}
        self.key = None
        self.value = None

        # Main layout will be self.grid_layout
        self.grid_layout = QGridLayout() # Changed from local 'layout' to instance 'self.grid_layout'
        self.setLayout(self.grid_layout)

        # UI Elements
        self.batch_selection_label = QLabel("选择试验批次：") # Made instance variable
        self.batch_selection_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        self.batch_selection_label.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #dee2e6;
            }
        """)
        
        self.selec = QComboBox() # Made instance variable
        self.selec.setFont(QFont("Microsoft YaHei", 10))
        self.selec.setStyleSheet("""
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
        
        self.view = QTableView() # Made instance variable
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setGridStyle(Qt.SolidLine)
        self.view.setFont(QFont("Microsoft YaHei", 9))

        header = self.view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        self.view.verticalHeader().setDefaultSectionSize(30)
        self.view.verticalHeader().setVisible(False)

        self.selec.currentTextChanged.connect(self.update_table)
        
        # Buttons
        self.print_button = QPushButton("打印") # Made instance variable
        self.print_button.clicked.connect(self.generate)
        self.print_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.print_button.setMaximumWidth(80); self.print_button.setMaximumHeight(45)
        # Assuming stylesheet remains similar or is handled
        self.print_button.setStyleSheet("QPushButton { border: 2px solid #4CAF50; border-radius: 6px; font-weight: bold; font-size: 12px; padding: 4px 8px; } QPushButton:hover { background-color: #f0f0f0; border-color: #45a049; } QPushButton:pressed { background-color: #e0e0e0; }")


        self.batch_print_button = QPushButton("批量生成所有报告") # Made instance variable
        self.batch_print_button.clicked.connect(self.generate_all_batches)
        self.batch_print_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.batch_print_button.setMaximumWidth(150); self.batch_print_button.setMaximumHeight(45)
        # Assuming stylesheet remains similar or is handled
        self.batch_print_button.setStyleSheet("QPushButton { border: 2px solid #007BFF; border-radius: 6px; font-weight: bold; font-size: 12px; padding: 4px 8px; background-color: #FFFFFF; color: #007BFF; } QPushButton:hover { background-color: #E7F3FF; border-color: #0056B3; } QPushButton:pressed { background-color: #CCE7FF; }")

        # Message Label for when table is not available
        self.message_label = QLabel("The 'tools' table does not exist or is empty.\nPlease import data via the 'Quick Start' tab.")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold)) # Adjusted font
        self.message_label.setStyleSheet("color: grey; padding: 20px;")
        self.message_label.setVisible(False) # Initially hidden

        # Add widgets to self.grid_layout
        self.grid_layout.addWidget(self.batch_selection_label, 0, 0)
        self.grid_layout.addWidget(self.selec, 0, 1, 1, 2)
        # Add message_label to occupy the same space as view, toggle visibility
        self.grid_layout.addWidget(self.message_label, 1, 0, 1, 3, Qt.AlignCenter)
        self.grid_layout.addWidget(self.view, 1, 0, 1, 3) # view will be shown/hidden by refresh_data
        self.grid_layout.addWidget(self.print_button, 2, 0, 1, 1, alignment=Qt.AlignRight)
        self.grid_layout.addWidget(self.batch_print_button, 2, 1, 1, 2, alignment=Qt.AlignLeft)
        
        self.grid_layout.setVerticalSpacing(15)
        self.grid_layout.setHorizontalSpacing(10)
        self.grid_layout.setContentsMargins(15, 15, 15, 15)
        self.grid_layout.setRowStretch(1, 1) # Main content area (table or message)
        self.grid_layout.setColumnStretch(1, 1) # Allow selec to stretch
        # self.grid_layout.setColumnStretch(2, 1) # This was likely for the third column of view

        # Initial data load
        self.refresh_data()

    def _update_ui_for_data_state(self, table_exists: bool, has_data_in_dic: bool):
        """Helper to manage visibility and enabled state of UI elements."""
        if not table_exists:
            self.message_label.setText("The 'tools' table does not exist in the database.\nPlease import data via the 'Quick Start' tab.")
            self.message_label.setVisible(True)
            self.batch_selection_label.setVisible(False)
            self.selec.setVisible(False)
            self.view.setVisible(False)
            self.print_button.setEnabled(False)
            self.batch_print_button.setEnabled(False)
        else:
            # self.message_label.setVisible(False) # This will be re-shown if no data in dic
            self.batch_selection_label.setVisible(True)
            self.selec.setVisible(True)
            # self.view.setVisible(True) # Visibility handled based on has_data_in_dic

            if has_data_in_dic:
                self.message_label.setVisible(False)
                self.view.setVisible(True)
                self.print_button.setEnabled(True)
                self.batch_print_button.setEnabled(True)
            else:
                self.message_label.setText("Data loaded, but no valid report batches found.\nCheck table content or import different data.")
                self.message_label.setVisible(True)
                self.view.setVisible(False)
                self.print_button.setEnabled(False)
                self.batch_print_button.setEnabled(False)

    def _clear_data_ui(self, clear_dic_map=True): # Unused, can be removed or adapted
        """Helper to clear UI elements related to data and optionally the data map."""
        self.view.setModel(None)
        self.selec.clear()
        if clear_dic_map:
            self.dic.clear()
        self.key = None
        self.value = None

    def refresh_data(self):
        print("ReportTab: Refreshing data...")
        try:
            if not self.db_manager.db.isOpen():
                if not self.db_manager.db.open():
                    QMessageBox.critical(self, "Database Error", f"Failed to open database: {self.db_manager.db.lastError().text()}")
                    self._update_ui_for_data_state(table_exists=False, has_data_in_dic=False)
                    self.dic.clear(); self.selec.clear(); self.view.setModel(None)
                    return

            table_exists = "tools" in self.db_manager.db.tables()

            if not table_exists:
                self.dic.clear(); self.selec.clear(); self.view.setModel(None)
                self._update_ui_for_data_state(table_exists=False, has_data_in_dic=False)
                return

            # Table exists, proceed
            db_path = self.db_manager.db.databaseName()
            # db_path check might be redundant if table_exists implies a valid db_path from an open db
            if not db_path or db_path == ":memory:":
                 QMessageBox.critical(self, "Database Error", "Invalid database path for existing table.")
                 self._update_ui_for_data_state(table_exists=False, has_data_in_dic=False)
                 return

            # Using read_sql_table for consistency with ExcelHandler's export, which uses SQLAlchemy
            from sqlalchemy import create_engine
            engine = create_engine(f"sqlite:///{db_path}")
            df = pd.read_sql_table("tools", engine)

            required_cols = ['委托单位', '样品名称', '接收日期']
            if not all(col in df.columns for col in required_cols):
                QMessageBox.warning(self, "Data Error", f"'tools' table is missing required columns for grouping: {', '.join(c for c in required_cols if c not in df.columns)}. Please re-import the data with correct columns.")
                self.dic.clear(); self.selec.clear(); self.view.setModel(None)
                self._update_ui_for_data_state(table_exists=True, has_data_in_dic=False)
                return

            if df.empty:
                print("ReportTab: 'tools' table is empty.")
                self.dic.clear()
            else:
                grouped_object = df.groupby(required_cols, sort=False) # sort=False to maintain original order if needed
                self.dic.clear()
                for name_tuple, group_df in grouped_object:
                    self.dic[name_tuple] = group_df

            self.selec.blockSignals(True)
            self.selec.clear()
            if self.dic:
                for key_tuple in self.dic.keys():
                    self.selec.addItem(str(key_tuple), key_tuple)
            self.selec.blockSignals(False)

            has_data_in_dic = bool(self.dic)
            self._update_ui_for_data_state(table_exists=True, has_data_in_dic=has_data_in_dic)

            if self.selec.count() > 0: # If batches were found and populated
                if self.selec.currentIndex() == 0: self.update_table() # Manually trigger if first item is already current
                else: self.selec.setCurrentIndex(0) # Triggers update_table via signal
            else: # No batches found (dic was empty or became empty)
                self.update_table() # Call to clear the table view / set key/value to None

            print(f"ReportTab: Data refreshed. {len(self.dic)} batches found.")

        except Exception as e:
            print(f"ReportTab: Error during data refresh: {e}")
            QMessageBox.critical(self, "Refresh Error", f"An error occurred while refreshing data: {e}")
            self.dic.clear(); self.selec.clear(); self.view.setModel(None)
            # Fallback to a state assuming table doesn't exist or data is unusable
            self._update_ui_for_data_state(table_exists=False, has_data_in_dic=False)


    def update_table(self):
        """Updates the QTableView model based on the current QComboBox selection."""
        current_key_tuple = self.selec.currentData()

        if current_key_tuple and isinstance(current_key_tuple, tuple) and current_key_tuple in self.dic:
            self.key = current_key_tuple
            self.value = self.dic[current_key_tuple]
            model = PandasModel(self.value)
            self.view.setModel(model)
        else:
            self.view.setModel(None)
            self.key = None
            self.value = None

    def generate(self):
        self.generator = ReportGenerator(self.key, self.value)
        self.generator.generate_report()

    def generate_all_batches(self):
        """批量生成所有批次的报告"""
        if not self.dic: # Check self.dic directly
            QMessageBox.warning(self, "警告", "没有可生成的批次数据")
            return
        
        total_count = len(self.dic)
        success_count = 0
        # Remainder of the method is assumed to be unchanged if it only relies on self.dic
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