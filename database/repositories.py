from database.connection import DBConnection
from core.models import Department, Employee, AdvanceRequest, Installment
from core.validators import AppLogger

class BaseRepository:
    def __init__(self):
        self.db = DBConnection()
        self.logger = AppLogger()

class DeptRepo(BaseRepository):
    def add(self, dept: Department):
        with self.db.get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO departments (name) VALUES (?)", (dept.name,))
            conn.commit()

    def get_all(self):
        with self.db.get_connection() as conn:
            return [Department(id=r[0], name=r[1]) for r in conn.execute("SELECT id, name FROM departments").fetchall()]

class EmpRepo(BaseRepository):
    def add(self, emp: Employee) -> bool:
        try:
            with self.db.get_connection() as conn:
                conn.execute("INSERT INTO employees (first_name, last_name, email, password, role, salary, department_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (emp.first_name, emp.last_name, emp.email, emp.password, emp.role, emp.salary, emp.department_id))
                conn.commit()
                return True
        except Exception: return False

    def delete(self, emp_id: int) -> bool:
        try:
            with self.db.get_connection() as conn:
                conn.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
                conn.commit()
                return True
        except Exception: return False

    def get_by_email(self, email: str):
        with self.db.get_connection() as conn:
            r = conn.execute("SELECT id, first_name, last_name, email, password, role, salary, department_id FROM employees WHERE email = ?", (email,)).fetchone()
            if r: return Employee(id=r[0], first_name=r[1], last_name=r[2], email=r[3], password=r[4], role=r[5], salary=r[6], department_id=r[7])
            return None

    def get_all(self):
        with self.db.get_connection() as conn:
            return [Employee(id=r[0], first_name=r[1], last_name=r[2], email=r[3], password=r[4], role=r[5], salary=r[6], department_id=r[7]) for r in conn.execute("SELECT * FROM employees").fetchall()]

class AdvanceRepo(BaseRepository):
    def add(self, adv: AdvanceRequest) -> bool:
        try:
            with self.db.get_connection() as conn:
                conn.execute("INSERT INTO advance_requests (employee_id, amount, requested_installments, reason, status, request_date, admin_note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (adv.employee_id, adv.amount, adv.requested_installments, adv.reason, adv.status, adv.request_date, adv.admin_note))
                conn.commit()
                return True
        except Exception: return False

    def update_status(self, req_id: int, status: str, admin_note: str) -> bool:
        try:
            with self.db.get_connection() as conn:
                conn.execute("UPDATE advance_requests SET status = ?, admin_note = ? WHERE id = ?", (status, admin_note, req_id))
                conn.commit()
                return True
        except Exception: return False

    def delete(self, req_id: int) -> bool:
        try:
            with self.db.get_connection() as conn:
                conn.execute("DELETE FROM advance_requests WHERE id = ?", (req_id,))
                conn.commit()
                return True
        except Exception: return False

    def get_all(self):
        with self.db.get_connection() as conn:
            return [AdvanceRequest(id=r[0], employee_id=r[1], amount=r[2], requested_installments=r[3], reason=r[4], status=r[5], request_date=r[6], admin_note=r[7]) for r in conn.execute("SELECT * FROM advance_requests").fetchall()]

class InstallmentRepo(BaseRepository):
    def add(self, inst: Installment) -> bool:
        try:
            with self.db.get_connection() as conn:
                conn.execute("INSERT INTO installments (advance_request_id, amount, due_date, is_paid) VALUES (?, ?, ?, ?)",
                             (inst.advance_request_id, inst.amount, inst.due_date, 1 if inst.is_paid else 0))
                conn.commit()
                return True
        except Exception: return False

    def get_by_advance_id(self, advance_id: int):
        with self.db.get_connection() as conn:
            return [Installment(id=r[0], advance_request_id=r[1], amount=r[2], due_date=r[3], is_paid=bool(r[4])) for r in conn.execute("SELECT * FROM installments WHERE advance_request_id = ?", (advance_id,)).fetchall()]