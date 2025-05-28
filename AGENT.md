# Agent Guidelines for 绝缘工器具检测系统 (V8)

## Commands
- **Run application**: `python main.py`
- **Install dependencies**: `pip install -r requirements.txt` (if exists)
- **Virtual environment**: `.venv` is configured (Python 3.13+)

## Project Structure
- `main.py` - Application entry point (PySide6)
- `ui/` - GUI components with tab-based interface
- `database/` - SQLite database management with Qt SQL models
- `utils/` - Excel processing and report generation utilities

## Code Style
- **Language**: Mixed Chinese/English (Chinese docstrings/comments, English code)
- **Imports**: PySide6 widgets grouped, relative imports for local modules
- **Classes**: CamelCase with descriptive Chinese class names where appropriate
- **Functions**: snake_case with Chinese docstrings
- **Database**: SQLite with `my_database.db` as default filename
- **Error handling**: Try-catch with Chinese error messages printed to console

## Key Dependencies
- PySide6 (Qt6 for Python) - GUI framework
- pandas - Excel file processing
- sqlite3 - Database operations
- docxtpl - Word document generation (inferred)

## Testing
- No formal test framework detected - manual testing via GUI
