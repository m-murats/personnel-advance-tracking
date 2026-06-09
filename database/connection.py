import sqlite3
from core.validators import AppLogger

class DBConnection:
    _instance = None

    def __new__(cls, db_name="hr_advance_system.db"):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            cls._instance.db_name = db_name
            cls._instance.logger = AppLogger()
            cls._instance._initialize_tables()
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize_tables(self):
        queries = [
            "CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)",
            """CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT NOT NULL, last_name TEXT NOT NULL, 
                email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, role TEXT NOT NULL, 
                salary REAL NOT NULL, department_id INTEGER, FOREIGN KEY(department_id) REFERENCES departments(id))""",
            """CREATE TABLE IF NOT EXISTS advance_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT, employee_id INTEGER, amount REAL NOT NULL,
                requested_installments INTEGER NOT NULL, reason TEXT, status TEXT NOT NULL, 
                request_date TEXT NOT NULL, admin_note TEXT,
                FOREIGN KEY(employee_id) REFERENCES employees(id))""",
            """CREATE TABLE IF NOT EXISTS installments (
                id INTEGER PRIMARY KEY AUTOINCREMENT, advance_request_id INTEGER,
                amount REAL NOT NULL, due_date TEXT NOT NULL, is_paid INTEGER NOT NULL,
                FOREIGN KEY(advance_request_id) REFERENCES advance_requests(id))"""
        ]
        with self.get_connection() as conn:
            for q in queries: conn.execute(q)
            conn.commit()