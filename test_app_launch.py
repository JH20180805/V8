import sys
from PySide6.QtWidgets import QApplication
# It's important that necessary modules are imported *before* MainWindow if they do setup
# that MainWindow relies on (like DB connection names or other global Qt settings).
from database.db_manager import DatabaseManager
from utils.excel_handler import ExcelHandler
from ui.main_window import MainWindow


if __name__ == '__main__':
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    # Initialize DatabaseManager. Under the new plan, this primarily sets up the
    # connection and doesn't create the 'tools' table with a schema.
    # No explicit db_mngr.db.close() here, as MainWindow will manage its own instance.
    print("Initializing DatabaseManager (outside MainWindow for initial setup if needed)...")
    try:
        # This ensures the db file can be created/accessed even before MainWindow fully initializes its own.
        # If my_database.db is purely managed by MainWindow's instance, this line isn't strictly necessary
        # for MainWindow to function but helps verify DatabaseManager's own __init__.
        initial_db_mngr = DatabaseManager()
        print(f"Database file '{initial_db_mngr.db.databaseName()}' should be accessible.")
        # We close this initial connection if it's not the one MainWindow will use,
        # to prevent locked db issues if MainWindow reopens.
        # However, QSqlDatabase uses named connections; if MainWindow uses the default
        # connection name, this might interfere. Let's assume MainWindow handles its own.
        initial_db_mngr.close() # Explicitly close this instance's connection
        print("Initial DatabaseManager connection closed.")
    except Exception as e:
        print(f"Error during initial DatabaseManager setup: {e}")
        sys.exit(1)


    print("Attempting to create MainWindow...")
    try:
        main_window = MainWindow()
        print("MainWindow created successfully.")
        # main_window.show() # .show() can cause issues in headless CI
        print("Smoke test passed: MainWindow instantiated.")
    except Exception as e:
        print(f"Error during MainWindow instantiation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    sys.exit(0)
