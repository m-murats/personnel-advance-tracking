import sys
import tkinter as tk
from tkinter import ttk
from gui.auth import LoginWindow
from core.validators import AppLogger
from database.repositories import DeptRepo, EmpRepo
from core.models import Department, Employee

def setup_defaults():
    dept_repo, emp_repo = DeptRepo(), EmpRepo()
    
    departments = [
        "Executive Management", "Human Resources", "Engineering", 
        "Finance & Accounting", "Sales & Marketing", "IT"
    ]
    for d in departments:
        dept_repo.add(Department(name=d))
        
    employees = emp_repo.get_all()
    has_admin = any(emp.role == "admin" for emp in employees)
    
    if not has_admin:
        admin = Employee("System", "Administrator", "admin@company.com", "admin123", "admin", 0.0, 1)
        emp_repo.add(admin)

def main():
    logger = AppLogger()
    logger.log_info("Enterprise HR System initializing...")
    try:
        setup_defaults()
        app = LoginWindow()
        
        style = ttk.Style(app)
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        app.mainloop()
    except Exception as e:
        logger.log_error(f"System Crash: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()