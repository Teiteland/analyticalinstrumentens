import sqlite3
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

DATABASE_PATH = "instruments.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS instruments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                model TEXT,
                manufacturer TEXT,
                serial_number TEXT,
                purchase_date TEXT,
                notes TEXT,
                status TEXT DEFAULT 'Active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                column_type TEXT,
                length_cm REAL,
                diameter_mm REAL,
                pore_size TEXT,
                install_date TEXT,
                status TEXT DEFAULT 'Active',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instrument_id) REFERENCES instruments(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                maintenance_type TEXT NOT NULL,
                description TEXT,
                performed_by TEXT,
                cost REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instrument_id) REFERENCES instruments(id) ON DELETE CASCADE
            )
        """)


class InstrumentRepository:
    @staticmethod
    def get_all(instrument_type: Optional[str] = None):
        with get_connection() as conn:
            if instrument_type:
                cursor = conn.execute("SELECT * FROM instruments WHERE type = ? ORDER BY name", (instrument_type,))
            else:
                cursor = conn.execute("SELECT * FROM instruments ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(instrument_id: int):
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM instruments WHERE id = ?", (instrument_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(name: str, instrument_type: str, model: str = None, manufacturer: str = None,
               serial_number: str = None, purchase_date: str = None, notes: str = None):
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO instruments (name, type, model, manufacturer, serial_number, purchase_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, instrument_type, model, manufacturer, serial_number, purchase_date, notes))
            return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    @staticmethod
    def update(instrument_id: int, name: str, instrument_type: str, model: str = None,
               manufacturer: str = None, serial_number: str = None, purchase_date: str = None,
               notes: str = None, status: str = "Active"):
        with get_connection() as conn:
            conn.execute("""
                UPDATE instruments
                SET name=?, type=?, model=?, manufacturer=?, serial_number=?, purchase_date=?, notes=?, status=?
                WHERE id=?
            """, (name, instrument_type, model, manufacturer, serial_number, purchase_date, notes, status, instrument_id))

    @staticmethod
    def delete(instrument_id: int):
        with get_connection() as conn:
            conn.execute("DELETE FROM instruments WHERE id = ?", (instrument_id,))

    @staticmethod
    def count():
        with get_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM instruments").fetchone()[0]


class ColumnRepository:
    @staticmethod
    def get_by_instrument(instrument_id: int):
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM columns WHERE instrument_id = ? ORDER BY name", (instrument_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_all():
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT c.*, i.name as instrument_name, i.type as instrument_type
                FROM columns c
                LEFT JOIN instruments i ON c.instrument_id = i.id
                ORDER BY c.name
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(column_id: int):
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM columns WHERE id = ?", (column_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(instrument_id: int, name: str, column_type: str = None, length_cm: float = None,
               diameter_mm: float = None, pore_size: str = None, install_date: str = None,
               notes: str = None):
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO columns (instrument_id, name, column_type, length_cm, diameter_mm, pore_size, install_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (instrument_id, name, column_type, length_cm, diameter_mm, pore_size, install_date, notes))
            return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    @staticmethod
    def update(column_id: int, name: str, column_type: str = None, length_cm: float = None,
               diameter_mm: float = None, pore_size: str = None, install_date: str = None,
               status: str = "Active", notes: str = None):
        with get_connection() as conn:
            conn.execute("""
                UPDATE columns
                SET name=?, column_type=?, length_cm=?, diameter_mm=?, pore_size=?, install_date=?, status=?, notes=?
                WHERE id=?
            """, (name, column_type, length_cm, diameter_mm, pore_size, install_date, status, notes, column_id))

    @staticmethod
    def delete(column_id: int):
        with get_connection() as conn:
            conn.execute("DELETE FROM columns WHERE id = ?", (column_id,))


class MaintenanceRepository:
    @staticmethod
    def get_by_instrument(instrument_id: int):
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM maintenance WHERE instrument_id = ? ORDER BY date DESC
            """, (instrument_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_recent(limit: int = 10):
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT m.*, i.name as instrument_name, i.type as instrument_type
                FROM maintenance m
                JOIN instruments i ON m.instrument_id = i.id
                ORDER BY m.date DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(maintenance_id: int):
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM maintenance WHERE id = ?", (maintenance_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(instrument_id: int, date: str, maintenance_type: str, description: str = None,
               performed_by: str = None, cost: float = None):
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO maintenance (instrument_id, date, maintenance_type, description, performed_by, cost)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (instrument_id, date, maintenance_type, description, performed_by, cost))
            return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    @staticmethod
    def update(maintenance_id: int, date: str, maintenance_type: str, description: str = None,
               performed_by: str = None, cost: float = None):
        with get_connection() as conn:
            conn.execute("""
                UPDATE maintenance
                SET date=?, maintenance_type=?, description=?, performed_by=?, cost=?
                WHERE id=?
            """, (date, maintenance_type, description, performed_by, cost, maintenance_id))

    @staticmethod
    def delete(maintenance_id: int):
        with get_connection() as conn:
            conn.execute("DELETE FROM maintenance WHERE id = ?", (maintenance_id,))


import csv
import os


def export_all_to_csv(export_dir: str):
    os.makedirs(export_dir, exist_ok=True)
    
    with get_connection() as conn:
        instruments = conn.execute("""
            SELECT name, type, model, manufacturer, serial_number, purchase_date, notes, status
            FROM instruments ORDER BY name
        """).fetchall()
        
        with open(os.path.join(export_dir, "instruments.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "type", "model", "manufacturer", "serial_number", "purchase_date", "notes", "status"])
            for row in instruments:
                writer.writerow([row["name"], row["type"], row["model"], row["manufacturer"], 
                               row["serial_number"], row["purchase_date"], row["notes"], row["status"]])
        
        columns = conn.execute("""
            SELECT i.name as instrument_name, c.name, c.column_type, c.length_cm, c.diameter_mm,
                   c.pore_size, c.install_date, c.status, c.notes
            FROM columns c
            JOIN instruments i ON c.instrument_id = i.id
            ORDER BY i.name, c.name
        """).fetchall()
        
        with open(os.path.join(export_dir, "columns.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["instrument_name", "name", "column_type", "length_cm", "diameter_mm",
                           "pore_size", "install_date", "status", "notes"])
            for row in columns:
                writer.writerow([row["instrument_name"], row["name"], row["column_type"],
                               row["length_cm"], row["diameter_mm"], row["pore_size"],
                               row["install_date"], row["status"], row["notes"]])
        
        maintenance = conn.execute("""
            SELECT i.name as instrument_name, m.date, m.maintenance_type, m.description,
                   m.performed_by, m.cost
            FROM maintenance m
            JOIN instruments i ON m.instrument_id = i.id
            ORDER BY i.name, m.date
        """).fetchall()
        
        with open(os.path.join(export_dir, "maintenance.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["instrument_name", "date", "maintenance_type", "description", "performed_by", "cost"])
            for row in maintenance:
                writer.writerow([row["instrument_name"], row["date"], row["maintenance_type"],
                               row["description"], row["performed_by"], row["cost"]])


def import_all_from_csv(import_dir: str):
    instruments_file = os.path.join(import_dir, "instruments.csv")
    columns_file = os.path.join(import_dir, "columns.csv")
    maintenance_file = os.path.join(import_dir, "maintenance.csv")
    
    instrument_map = {}
    
    with get_connection() as conn:
        if os.path.exists(instruments_file):
            with open(instruments_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    serial = row.get("serial_number", "").strip()
                    
                    if serial:
                        existing = conn.execute(
                            "SELECT id FROM instruments WHERE serial_number = ?", (serial,)
                        ).fetchone()
                        
                        if existing:
                            conn.execute("""
                                UPDATE instruments SET name=?, type=?, model=?, manufacturer=?,
                                purchase_date=?, notes=?, status=?
                                WHERE serial_number=?
                            """, (row["name"], row["type"], row.get("model"), row.get("manufacturer"),
                                  row.get("purchase_date"), row.get("notes"), row.get("status", "Active"), serial))
                            instrument_map[row["name"]] = existing["id"]
                        else:
                            cursor = conn.execute("""
                                INSERT INTO instruments (name, type, model, manufacturer, serial_number, purchase_date, notes, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (row["name"], row["type"], row.get("model"), row.get("manufacturer"),
                                  serial, row.get("purchase_date"), row.get("notes"), row.get("status", "Active")))
                            instrument_map[row["name"]] = cursor.lastrowid
                    else:
                        cursor = conn.execute("""
                            INSERT INTO instruments (name, type, model, manufacturer, serial_number, purchase_date, notes, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (row["name"], row["type"], row.get("model"), row.get("manufacturer"),
                              serial, row.get("purchase_date"), row.get("notes"), row.get("status", "Active")))
                        instrument_map[row["name"]] = cursor.lastrowid
        
        if os.path.exists(columns_file):
            with open(columns_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    instrument_name = row.get("instrument_name", "").strip()
                    if instrument_name and instrument_name in instrument_map:
                        instrument_id = instrument_map[instrument_name]
                        
                        conn.execute("DELETE FROM columns WHERE instrument_id = ?", (instrument_id,))
                        
                        conn.execute("""
                            INSERT INTO columns (instrument_id, name, column_type, length_cm, diameter_mm, pore_size, install_date, status, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (instrument_id, row["name"], row.get("column_type"),
                              float(row["length_cm"]) if row.get("length_cm") else None,
                              float(row["diameter_mm"]) if row.get("diameter_mm") else None,
                              row.get("pore_size"), row.get("install_date"),
                              row.get("status", "Active"), row.get("notes")))
        
        if os.path.exists(maintenance_file):
            with open(maintenance_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    instrument_name = row.get("instrument_name", "").strip()
                    if instrument_name and instrument_name in instrument_map:
                        instrument_id = instrument_map[instrument_name]
                        
                        conn.execute("DELETE FROM maintenance WHERE instrument_id = ?", (instrument_id,))
                        
                        conn.execute("""
                            INSERT INTO maintenance (instrument_id, date, maintenance_type, description, performed_by, cost)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (instrument_id, row["date"], row["maintenance_type"],
                              row.get("description"), row.get("performed_by"),
                              float(row["cost"]) if row.get("cost") else None))
