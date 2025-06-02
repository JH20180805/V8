from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QMessageBox, QHeaderView, QStyledItemDelegate, QFileDialog, QLabel # Added QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlTableModel, QSqlDatabase
from PySide6.QtGui import QFont
from database.db_manager import DatabaseManager
from utils.excel_handler import ExcelHandler

class CenterAlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter

class ToolTab(QWidget):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

        layout = QVBoxLayout(self)

        # Initialize the model (without setting table yet)
        self.model = QSqlTableModel(db=self.db_manager.get_qt_connection())

        # Setup TableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model) # Model is set here
        self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setGridStyle(Qt.SolidLine)
        self.table_view.setFont(QFont("Microsoft YaHei", 9))
        
        header = self.table_view.horizontalHeader()
        # Changed from ResizeToContents to Interactive to allow user resizing and prevent content-based expansion
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True) # Keep last section stretched
        self.table_view.verticalHeader().setDefaultSectionSize(30)
        
        center_delegate = CenterAlignDelegate()
        self.table_view.setItemDelegate(center_delegate)
        layout.addWidget(self.table_view)

        # Setup Message Label (for when table is not available)
        self.message_label = QLabel("The 'tools' table does not exist in the database.\nPlease import data via the 'Quick Start' tab to create and populate the table.")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setFont(QFont("Microsoft YaHei", 10))
        self.message_label.setStyleSheet("color: grey; padding: 10px;") # Added padding
        self.message_label.setWordWrap(True)
        # Policy: Expanding horizontally, preferred vertically (adjusts to content height)
        self.message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.message_label) # Add to layout, visibility will be toggled

        # UI Elements for Editing
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("添加行") # Changed from "Add Row"
        self.delete_button = QPushButton("删除行") # Changed from "Delete Row"
        self.export_button = QPushButton("导出到Excel") # Changed from "Export to Excel"
        self.save_button = QPushButton("保存更改") # Changed from "Save Changes"
        self.revert_button = QPushButton("撤销更改") # Changed from "Revert Changes"

        # Apply compact styling to buttons
        compact_font = QFont("Microsoft YaHei", 9) # Or another suitable font
        buttons_to_style = [
            self.add_button,
            self.delete_button,
            self.save_button,
            self.revert_button,
            self.export_button
        ]

        for button in buttons_to_style:
            button.setFont(compact_font)
            # Override global style for padding and set a max width
            # Keep other aspects of default button styling if possible,
            # or define a more complete stylesheet if needed.
            button.setStyleSheet("padding: 4px 8px; margin: 2px;") # Reduced padding, small margin
            button.setMaximumWidth(130) # Max width for these buttons

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.revert_button)
        layout.addLayout(button_layout)

        # Connect Buttons to Model Actions
        self.add_button.clicked.connect(self.addRow)
        self.delete_button.clicked.connect(self.deleteRow)
        self.save_button.clicked.connect(self.saveChanges)
        self.revert_button.clicked.connect(self.revertChanges)
        self.export_button.clicked.connect(self.export_data_to_excel)

        # Initial data load and UI state setup
        self.refresh_data()

    def set_controls_enabled(self, enabled: bool):
        """Enable or disable all data manipulation buttons."""
        self.add_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.revert_button.setEnabled(enabled)
        self.export_button.setEnabled(enabled) # Export also depends on table existing

    def refresh_data(self):
        """
        Refreshes the data in the table view.
        Checks if the 'tools' table exists and updates UI accordingly.
        """
        # Check if the database connection is open, open it if not.
        if not self.db_manager.db.isOpen():
            if not self.db_manager.db.open():
                QMessageBox.critical(self, "Database Error", f"Failed to open database: {self.db_manager.db.lastError().text()}")
                self.table_view.setVisible(False)
                self.message_label.setText("Database connection failed. Cannot load data.")
                self.message_label.setVisible(True)
                self.set_controls_enabled(False)
                return

        table_exists = "tools" in self.db_manager.get_qt_connection().tables()

        if not table_exists:
            print("ToolTab: 'tools' table not found.")
            self.table_view.setVisible(False)
            self.message_label.setText("The 'tools' table does not exist.\nPlease import data via 'Quick Start' tab.")
            self.message_label.setVisible(True)
            self.model.clear() # Clear any existing model data/structure
            self.set_controls_enabled(False)
        else:
            print("ToolTab: 'tools' table found. Loading data.")
            self.table_view.setVisible(True)
            self.message_label.setVisible(False)
            self.set_controls_enabled(True)

            self.model.setTable("tools") # Set the table for the model
            self.model.setEditStrategy(QSqlTableModel.OnRowChange) # Set edit strategy

            if not self.model.select(): # Perform the data selection
                # Restore QMessageBox for user feedback
                QMessageBox.critical(self, "Data Refresh Error",
                                     f"Could not load data from 'tools' table: {self.model.lastError().text()}")
                print(f"ToolTab: Error loading data: {self.model.lastError().text()}")
                # Potentially disable controls or show message label again if select fails badly
                # self.table_view.setVisible(False)
                # self.message_label.setText("Error loading data from 'tools' table.")
                # self.message_label.setVisible(True)
                # self.set_controls_enabled(False)
            elif self.model.rowCount() == 0:
                print("ToolTab: Data loaded, but 'tools' table is empty.")
                # Table exists and is empty, controls should still be enabled for adding rows.
            else:
                print("ToolTab: Data loaded successfully.")

    def addRow(self):
        # This action should only be possible if controls are enabled (table exists)
        rowCount = self.model.rowCount()
        self.model.insertRow(rowCount)
        self.table_view.scrollToBottom()

    def deleteRow(self):
        currentRow = self.table_view.currentIndex().row()
        if currentRow >= 0:
            self.model.removeRow(currentRow)
            # Consider if model needs manual refresh after row removal if OnRowChange is not immediate enough
            # For now, rely on OnRowChange and subsequent save/revert to finalize.
            # A self.model.select() here would discard unsaved changes on other rows.
        else:
            QMessageBox.warning(self, "No Row Selected", "Please select a row to delete.")

    def saveChanges(self):
        if self.model.submitAll():
            QMessageBox.information(self, "Changes Saved", "Your changes have been saved successfully.")
            self.refresh_data() # Refresh to show any backend-triggered changes or ensure consistency
        else:
            QMessageBox.critical(self, "Save Failed",
                                 f"Could not save changes: {self.model.lastError().text()}")

    def revertChanges(self):
        self.model.revertAll()
        QMessageBox.information(self, "Changes Reverted", "All pending changes have been reverted.")
        self.refresh_data() # Refresh to show original state

    def export_data_to_excel(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)", options=options
        )
        if fileName:
            if not fileName.endswith(".xlsx"):
                fileName += ".xlsx"
            excel_handler = ExcelHandler(self.db_manager)
            success = excel_handler.export_to_excel("tools", fileName)
            if success:
                QMessageBox.information(self, "Export Successful", f"Data successfully exported to:\n{fileName}")
            else:
                QMessageBox.warning(self, "Export Failed", "Could not export data to Excel. Check console/logs for details.")

# Keep __main__ for standalone testing if desired, but ensure it reflects changes
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    class DummyDBManager:
        def __init__(self, create_table=True): # Option to simulate table not existing
            self.db = QSqlDatabase.addDatabase("QSQLITE", f"dummy_tools_tab_conn_{id(self)}")
            self.db_name = f"dummy_tools_test_{id(self)}.db"
            self.db.setDatabaseName(self.db_name)
            if not self.db.open():
                print(f"DummyDBManager: Failed to open database: {self.db.lastError().text()}")
            else:
                print("DummyDBManager: Database opened successfully.")
                if create_table:
                    self._create_tools_table()
                else:
                    # Ensure table does not exist for testing "table not found" state
                    query = QSqlQuery(self.db)
                    query.exec_("DROP TABLE IF EXISTS tools")
                    print("DummyDBManager: Ensured 'tools' table does not exist for this test.")


        def get_qt_connection(self):
            return self.db

        def _create_tools_table(self):
            from PySide6.QtSql import QSqlQuery
            query = QSqlQuery(self.db)
            if "tools" not in self.db.tables(): # Check before creating
                create_sql = """CREATE TABLE tools (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, value TEXT);"""
                if not query.exec_(create_sql): # Use exec_ for consistency
                    print(f"DummyDBManager: Failed to create 'tools' table: {query.lastError().text()}")
                else:
                    print("DummyDBManager: 'tools' table created.")
                    query.exec_("INSERT INTO tools (name, value) VALUES ('Sample1', 'Value1')")
                    query.exec_("INSERT INTO tools (name, value) VALUES ('Sample2', 'Value2')")
            else:
                 print("DummyDBManager: 'tools' table already exists.")

        def close(self):
            if self.db.isOpen():
                self.db.close()
            QSqlDatabase.removeDatabase(f"dummy_tools_tab_conn_{id(self)}")
            # import os
            # if os.path.exists(self.db_name):
            #     os.remove(self.db_name) # Clean up dummy db file
            print(f"DummyDBManager: Database '{self.db_name}' closed and connection removed.")

    # Test case 1: Table exists
    print("\n--- Test Case 1: Table Exists ---")
    db_m_exists = DummyDBManager(create_table=True)
    main_window_exists = ToolTab(db_m_exists)
    main_window_exists.setWindowTitle("ToolTab Test - Table Exists")
    main_window_exists.show()

    # Test case 2: Table does NOT exist
    # For this to run after the first, QApplication needs to be managed carefully,
    # or run them separately. For now, just showing setup.
    # To run this properly, the QApplication should only be exec'd once.
    # This example __main__ will show the first window, then the second will replace it if app.exec() is at the very end.

    # print("\n--- Test Case 2: Table Does Not Exist ---")
    # db_m_not_exists = DummyDBManager(create_table=False)
    # main_window_not_exists = ToolTab(db_m_not_exists)
    # main_window_not_exists.setWindowTitle("ToolTab Test - Table Missing")
    # main_window_not_exists.show() # This would be the active window if both are shown before app.exec()

    sys.exit(app.exec())
    # db_m_exists.close() # Close DBs after app exits
    # db_m_not_exists.close()
