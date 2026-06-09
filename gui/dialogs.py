import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date
from core.validators import DataValidator, SessionManager
from core.models import Employee, AdvanceRequest, Installment
from database.repositories import EmpRepo, DeptRepo, AdvanceRepo, InstallmentRepo

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, [31,29 if year%4==0 and not year%400==0 else 28,31,30,31,30,31,31,30,31,30,31][month-1])
    return date(year, month, day)

class BaseDialog(tk.Toplevel):
    def __init__(self, parent, title, geometry="400x500"):
        super().__init__(parent)
        self.title(title)
        self.geometry(geometry)
        self.configure(padx=20, pady=20)
        self.grab_set()
        self.build_ui()

    def build_ui(self): raise NotImplementedError

class EmployeeDialog(BaseDialog):
    def __init__(self, parent):
        self.emp_repo, self.dept_repo = EmpRepo(), DeptRepo()
        super().__init__(parent, "Add New Personnel", "350x550")

    def build_ui(self):
        ttk.Label(self, text="Personnel Details", font=("Helvetica", 14, "bold")).pack(pady=(0, 15))
        
        fields = ["First Name:", "Last Name:", "Email:", "Password:", "Role:", "Base Salary:", "Department:"]
        self.entries = {}
        
        for f in fields:
            ttk.Label(self, text=f).pack(anchor="w")
            if f == "Role:":
                cb = ttk.Combobox(self, values=["employee", "admin"], state="readonly")
                cb.pack(fill="x", pady=(0, 10))
                cb.current(0)
                cb.bind("<<ComboboxSelected>>", self.toggle_salary)
                self.entries[f] = cb
            elif f == "Department:":
                depts = self.dept_repo.get_all()
                cb = ttk.Combobox(self, values=[d.name for d in depts], state="readonly")
                cb.pack(fill="x", pady=(0, 10))
                if depts: cb.current(0)
                self.entries[f] = cb
                self.departments = depts
            elif f == "Password:":
                e = ttk.Entry(self, show="*")
                e.pack(fill="x", pady=(0, 10))
                self.entries[f] = e
            else:
                e = ttk.Entry(self)
                e.pack(fill="x", pady=(0, 10))
                self.entries[f] = e

        ttk.Button(self, text="Save Personnel", command=self.save).pack(pady=15, fill="x")

    def toggle_salary(self, event=None):
        role = self.entries["Role:"].get()
        salary_entry = self.entries["Base Salary:"]
        if role == "admin":
            salary_entry.delete(0, tk.END)
            salary_entry.insert(0, "0.0")
            salary_entry.config(state="disabled")
        else:
            salary_entry.config(state="normal")
            if salary_entry.get() == "0.0":
                salary_entry.delete(0, tk.END)

    def save(self):
        if not DataValidator.is_valid_email(self.entries["Email:"].get()):
            return messagebox.showerror("Error", "Invalid email.")
            
        role = self.entries["Role:"].get()
        salary_str = self.entries["Base Salary:"].get()
        
        if role == "admin":
            salary = 0.0
        else:
            if not DataValidator.is_positive_float(salary_str):
                return messagebox.showerror("Error", "Base Salary must be a positive number.")
            salary = float(salary_str)

        dept_id = next(d.id for d in self.departments if d.name == self.entries["Department:"].get())
        emp = Employee(
            first_name=self.entries["First Name:"].get(), last_name=self.entries["Last Name:"].get(), 
            email=self.entries["Email:"].get(), password=self.entries["Password:"].get(), 
            role=role, salary=salary, department_id=dept_id
        )
        if self.emp_repo.add(emp):
            messagebox.showinfo("Success", "Personnel successfully added to the system.")
            self.destroy()

class AdvanceReqDialog(BaseDialog):
    def __init__(self, parent):
        self.adv_repo = AdvanceRepo()
        super().__init__(parent, "Request Advance", "350x350")

    def build_ui(self):
        ttk.Label(self, text="Advance Request Form", font=("Helvetica", 14, "bold")).pack(pady=(0, 15))
        
        ttk.Label(self, text="Requested Amount ($):").pack(anchor="w")
        self.amount_entry = ttk.Entry(self)
        self.amount_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(self, text="Requested Installments (Months):").pack(anchor="w")
        self.inst_entry = ttk.Entry(self)
        self.inst_entry.insert(0, "1")
        self.inst_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(self, text="Reason for Advance:").pack(anchor="w")
        self.reason_entry = ttk.Entry(self)
        self.reason_entry.pack(fill="x", pady=(0, 10))

        ttk.Button(self, text="Submit Request", command=self.save).pack(pady=20, fill="x")

    def save(self):
        user = SessionManager().get_user()
        amount_str = self.amount_entry.get()
        inst_str = self.inst_entry.get()
        
        if not DataValidator.is_positive_float(amount_str): return messagebox.showerror("Error", "Invalid amount.")
        try:
            requested_inst = int(inst_str)
            if requested_inst <= 0: raise ValueError
        except ValueError:
            return messagebox.showerror("Error", "Installments must be a positive integer.")
            
        adv = AdvanceRequest(
            employee_id=user.id, amount=float(amount_str), requested_installments=requested_inst,
            reason=self.reason_entry.get(), status="Pending", request_date=str(date.today())
        )
        if self.adv_repo.add(adv):
            messagebox.showinfo("Success", "Request sent to Admin.")
            self.destroy()

class ReviewDialog(BaseDialog):
    def __init__(self, parent, advance_req):
        self.adv_repo = AdvanceRepo()
        self.inst_repo = InstallmentRepo()
        self.req = advance_req
        super().__init__(parent, "Review Advance Request", "400x480")

    def build_ui(self):
        ttk.Label(self, text="Admin Review Panel", font=("Helvetica", 14, "bold")).pack(pady=(0, 15))
        
        info_frame = ttk.LabelFrame(self, text="Request Details", padding=10)
        info_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(info_frame, text=f"Amount: ${self.req.amount:,.2f}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Reason: {self.req.reason}").pack(anchor="w")
        
        # DÜZELTİLEN SATIR: foreground="blue" artık Label'ın içinde!
        ttk.Label(info_frame, text=f"Req. Installments: {self.req.requested_installments} Months", foreground="blue").pack(anchor="w")
        
        ttk.Label(info_frame, text=f"Date: {self.req.request_date}").pack(anchor="w")

        ttk.Label(self, text="Admin Note / Feedback:").pack(anchor="w")
        self.note_entry = ttk.Entry(self)
        self.note_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(self, text="Decision:").pack(anchor="w")
        self.action_combo = ttk.Combobox(self, values=["Approve", "Reject"], state="readonly")
        self.action_combo.pack(fill="x", pady=(0, 10))
        self.action_combo.current(0)
        self.action_combo.bind("<<ComboboxSelected>>", self.toggle_installment)

        self.inst_label = ttk.Label(self, text="Approved Installments (Override if needed):")
        self.inst_label.pack(anchor="w")
        self.months_entry = ttk.Entry(self)
        self.months_entry.insert(0, str(self.req.requested_installments))
        self.months_entry.pack(fill="x", pady=(0, 15))

        ttk.Button(self, text="Confirm Decision", command=self.save).pack(fill="x")

    def toggle_installment(self, event):
        # Kutu devre dışı bırakma işlemini en stabil yöntemle yapıyoruz
        if self.action_combo.get() == "Reject":
            self.months_entry.config(state="disabled")
        else:
            self.months_entry.config(state="normal")

    def save(self):
        action = self.action_combo.get()
        status = "Approved" if action == "Approve" else "Rejected"
        
        if self.adv_repo.update_status(self.req.id, status, self.note_entry.get()):
            if status == "Approved":
                try:
                    months = int(self.months_entry.get())
                    if months <= 0: raise ValueError
                    inst_amount = self.req.amount / months
                    for i in range(months):
                        due = add_months(date.today(), i+1)
                        self.inst_repo.add(Installment(advance_request_id=self.req.id, amount=inst_amount, due_date=str(due), is_paid=False))
                except ValueError:
                    return messagebox.showerror("Error", "Invalid installment months.")
            messagebox.showinfo("Success", f"Request successfully {status}.")
            self.destroy()