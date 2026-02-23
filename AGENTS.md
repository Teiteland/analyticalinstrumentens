# Instrumentoversikt (Instrument Overview)

A desktop GUI application for managing laboratory chromatographic instruments (LC, GC, GPC). Built with Python, customtkinter, and SQLite.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| GUI Framework | customtkinter 5.2.2 |
| Database | SQLite |
| Architecture | MVC with Repository pattern |

## Project Structure

```
instrumentoversiktguilog/
├── app.py           # Main GUI application - all UI logic
├── database.py      # Database layer - repositories & schema
├── main.py          # Entry point
├── requirements.txt # Python dependencies
├── README.md        # User documentation (Norwegian)
├── SPEC.md          # Detailed specification
└── instruments.db   # SQLite database (auto-created)
```

## Setup & Running

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Architecture

### Database Layer (`database.py`)

- **Tables**: `instruments`, `columns`, `maintenance`
- **Repository Pattern**: `InstrumentRepository`, `ColumnRepository`, `MaintenanceRepository`
- **Connection**: Context manager `get_connection()` for safe SQLite handling
- **CSV Operations**: Export/import functions

### UI Layer (`app.py`)

- Single-window application with sidebar navigation
- Main `InstrumentApp` class manages all views
- Modal dialogs for add/edit operations
- Dark theme (customtkinter default)

### Entry Point (`main.py`)

Simple launcher that imports and runs `InstrumentApp`.

## Common Tasks

### Adding a New Instrument Type

To add a new instrument type (e.g., "IC" for Ion Chromatography):

1. **Update `database.py`**:
   - Add the new type to the type validation in `InstrumentRepository.insert()`
   - Update the `get_instruments_by_type()` method to include the new type

2. **Update `app.py`**:
   - Add the new type to the `INSTRUMENT_TYPES` tuple/list (around line where types are defined)
   - Add a filter button in the sidebar (see existing LC/GC/GPC buttons)
   - Update the dashboard statistics to include the new type

3. **Test**:
   - Run the app and verify the new type appears in filters
   - Try adding an instrument with the new type

### Adding a New Field to Instruments

1. **Update `database.py`**:
   - Add the column to the `create_tables()` function
   - Update `InstrumentRepository.insert()` to accept the new field
   - Update `InstrumentRepository.update()` to modify the field
   - Update the model (returned dictionary) in relevant methods

2. **Update `app.py`**:
   - Add input field in the instrument dialog (add/edit form)
   - Update the display in instrument detail view if applicable
   - Handle the new field in CSV import/export if needed

### Modifying CSV Import/Export

CSV functions are in `database.py`:

- `export_instruments_csv()` - Exports all instruments
- `export_columns_csv()` - Exports all columns
- `export_maintenance_csv()` - Exports all maintenance records
- `import_instruments_csv()` - Imports with upsert logic (matches by serial_number)

To modify the CSV format:
1. Update the fieldnames in the export functions
2. Update the expected columns in the import function
3. Handle any new fields in the import mapping

### Adding a New View/Tab

1. Add navigation button in sidebar (in `setup_sidebar()` method)
2. Create new method to build the view frame
3. Add view switching logic in the navigation method
4. Consider using the existing table/grid pattern for consistency

## Code Conventions

- **Language**: English for code and comments
- **UI Language**: Norwegian (user-facing text in the application)
- **Database**: SQLite with repository pattern
- **Error Handling**: Basic try/except in UI layer, let database errors propagate
- **No Tests**: Manual testing through the GUI

## Database Schema

### instruments
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Instrument name |
| type | TEXT | LC, GC, or GPC |
| model | TEXT | Model name |
| manufacturer | TEXT | Manufacturer |
| serial_number | TEXT | Serial number (unique for import) |
| purchase_date | TEXT | ISO date |
| notes | TEXT | Additional notes |
| status | TEXT | Status (e.g., " aktiv", " decommissioned") |
| created_at | TEXT | Timestamp |

### columns
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| instrument_id | INTEGER | Foreign key to instruments |
| name | TEXT | Column name |
| column_type | TEXT | Column type |
| length_cm | REAL | Length in cm |
| diameter_mm | REAL | Diameter in mm |
| pore_size | TEXT | Pore size |
| install_date | TEXT | ISO date |
| status | TEXT | Status |
| notes | TEXT | Additional notes |
| created_at | TEXT | Timestamp |

### maintenance
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| instrument_id | INTEGER | Foreign key to instruments |
| date | TEXT | Maintenance date |
| maintenance_type | TEXT | Type of maintenance |
| description | TEXT | Description |
| performed_by | TEXT | Who performed it |
| cost | REAL | Cost |
| created_at | TEXT | Timestamp |

## Debugging

- Database file: `instruments.db` in project root
- To inspect: `sqlite3 instruments.db`
- To reset: Delete `instruments.db` and restart (will recreate)
