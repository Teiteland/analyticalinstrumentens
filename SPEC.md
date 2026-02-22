# Instrumentoversikt - Laboratory Instrument Tracking GUI

## 1. Project Overview

- **Project name**: Instrumentoversikt
- **Type**: Desktop GUI Application (Python/customtkinter)
- **Core functionality**: Track chromatographic instruments (LC, GC, GPC), their columns, maintenance history, and purchase dates in an analytical laboratory
- **Target users**: Laboratory technicians and managers

## 2. UI/UX Specification

### Layout Structure

- **Main Window**: Single window with sidebar navigation (800x600 minimum, resizable)
- **Navigation Sidebar**: Left side, dark background, with menu items
- **Content Area**: Right side, displays current view
- **Dialogs**: Modal dialogs for add/edit operations

### Visual Design

- **Theme**: Modern dark theme using customtkinter default
- **Color Palette**:
  - Primary: Blue (#3B8ED0)
  - Secondary: Dark gray (#1f1f1f)
  - Accent: Green for success, Red for alerts
  - Text: White/Light gray
- **Typography**: System default (Segoe UI on Windows, SF Pro on macOS, Ubuntu on Linux)
- **Spacing**: 10px padding standard, 5px for tight elements

### Components

1. **Sidebar Navigation**
   - Dashboard (home)
   - LC Instruments
   - GC Instruments
   - GPC Instruments
   - All Columns
   - Settings

2. **Instrument List View**
   - Table showing: Name, Model, Serial Number, Purchase Date, Status
   - Add button, Edit button, Delete button
   - Search/filter functionality

3. **Instrument Detail View**
   - General info (name, model, serial, purchase date)
   - Attached columns list
   - Maintenance history
   - Add column button, Add maintenance button

4. **Column List View**
   - Table showing: Name, Type, Dimensions, Instrument, Install Date, Status
   - Add/Edit/Delete buttons

5. **Maintenance Record View**
   - Table showing: Date, Type, Description, Performed By, Cost
   - Add maintenance record

## 3. Functionality Specification

### Core Features

1. **Instrument Management**
   - Add new LC, GC, or GPC instrument
   - Edit instrument details
   - Delete instrument (with confirmation)
   - View instrument list filtered by type
   - Fields: Name, Type (LC/GC/GPC), Model, Manufacturer, Serial Number, Purchase Date, Notes

2. **Column Management**
   - Add column to instrument
   - Edit column details
   - Remove column from instrument
   - Track column status (Active, In Storage, Retired)
   - Fields: Name, Type (e.g., C18, DB-5ms), Dimensions (L x D), Pore Size, Install Date, Notes

3. **Maintenance Tracking**
   - Add maintenance record to instrument
   - Edit maintenance record
   - View maintenance history
   - Fields: Date, Type (Preventive, Repair, Calibration, Other), Description, Performed By, Cost

4. **Dashboard**
   - Overview of all instruments
   - Quick stats: Total instruments, instruments needing attention
   - Recent maintenance records

### Data Handling

- **Storage**: SQLite database (instruments.db)
- **Auto-save**: Changes saved immediately
- **Data validation**: Required fields, date format validation

### Edge Cases

- Empty database on first run
- Deleting instrument with columns (cascade delete or warn)
- Invalid date formats
- Duplicate instrument names (allowed, use ID)

## 4. Acceptance Criteria

1. Application launches without errors
2. Can add, edit, delete LC instruments
3. Can add, edit, delete GC instruments
4. Can add, edit, delete GPC instruments
5. Can add columns to instruments
6. Can add maintenance records to instruments
7. Data persists after application restart
8. Navigation between all views works
9. Dashboard shows correct statistics
