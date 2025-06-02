import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
# from database.db_manager import DatabaseManager # MainWindow creates its own instance
# from utils.excel_handler import ExcelHandler # Imported by main_window

if __name__ == '__main__':
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    # DatabaseManager is initialized within MainWindow.
    # The db_manager in MainWindow will handle table creation.
    # print("Initializing DatabaseManager for test setup...")
    # db_mngr = DatabaseManager()
    # print("DatabaseManager initialized.")

    print("Attempting to create MainWindow...")
    try:
        main_window = MainWindow()
        print("MainWindow created successfully.")
        # The MainWindow constructor calls setup_ui, which connects tab_widget.currentChanged
        # This signal is emitted when tabs are added and a default tab is set,
        # potentially triggering on_tab_changed for the initial tab.
        print("Smoke test passed: MainWindow instantiated.")
    except Exception as e:
        print(f"Error during MainWindow instantiation or showing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) # Indicate failure

    sys.exit(0) # Indicate success
