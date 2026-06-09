import tkinter as tk
from tkinter import ttk, messagebox
from core.validators import SessionManager
from database.repositories import EmpRepo, AdvanceRepo, InstallmentRepo
from core.services import PayrollService
from gui.dialogs import EmployeeDialog, AdvanceReqDialog, ReviewDialog

class AdminDashboard(ttk.Frame):
    def __init__(self, parent, logout_cb):
        super().__init__(parent, padding=10)
        self.logout_cb = logout_cb
        self.emp_repo = EmpRepo()
        self.adv_repo = AdvanceRepo()
        self.inst_repo = InstallmentRepo()  # Taksitleri saymak için eklendi
        self.payroll = PayrollService()
        self.build_ui()

    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Executive Admin Dashboard", font=("Helvetica", 18, "bold")).pack(side="left")
        
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side="right")
        ttk.Button(btn_frame, text="Log Out", command=self.logout_cb).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="↻ Refresh", command=self.refresh).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="+ Add Personnel", command=self.add_emp).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="- Fire Personnel", command=self.fire_emp).pack(side="right", padx=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.emp_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.emp_frame, text="Personnel & Payroll")
        columns = ("ID", "Name", "Role", "Base Salary", "Deductions (This Month)", "Net Salary")
        self.emp_tree = ttk.Treeview(self.emp_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns: self.emp_tree.heading(col, text=col)
        self.emp_tree.pack(expand=True, fill="both")

        self.req_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.req_frame, text="Advance Requests History") # İsim düzeltildi
        
        # YENİ SÜTUN: Appr. Inst. (Approved Installments - Onaylanan Taksit)
        req_columns = ("Req ID", "Emp ID", "Amount", "Req. Inst.", "Appr. Inst.", "Reason (Employee)", "Admin Note", "Status", "Date")
        self.req_tree = ttk.Treeview(self.req_frame, columns=req_columns, show="headings", selectmode="browse")
        for col in req_columns: self.req_tree.heading(col, text=col)
        self.req_tree.column("Req ID", width=50)
        self.req_tree.column("Emp ID", width=50)
        self.req_tree.column("Req. Inst.", width=70)
        self.req_tree.column("Appr. Inst.", width=70)
        self.req_tree.pack(expand=True, fill="both", pady=(0, 10))

        action_panel = ttk.LabelFrame(self.req_frame, text="Action Panel", padding=10)
        action_panel.pack(fill="x")
        ttk.Label(action_panel, text="Select a 'Pending' request from the table above, then click Review.").pack(side="left")
        ttk.Button(action_panel, text="Review Selected Request", command=self.review_selected).pack(side="right")

        self.refresh()

    def review_selected(self):
        selected = self.req_tree.selection()
        if not selected: return messagebox.showwarning("Warning", "Please select a request first.")
        
        req_id_from_tree = str(self.req_tree.item(selected[0])['values'][0])
        req = next((r for r in self.adv_repo.get_all() if str(r.id) == req_id_from_tree), None)
        
        if req and req.status == "Pending":
            ReviewDialog(self, req)
            self.refresh()
        else:
            messagebox.showinfo("Info", "Only 'Pending' requests can be reviewed.")

    def add_emp(self):
        EmployeeDialog(self)
        self.refresh()

    def fire_emp(self):
        selected = self.emp_tree.selection()
        if not selected: return messagebox.showwarning("Warning", "Select an employee to fire.")
        
        item_values = self.emp_tree.item(selected[0])['values']
        emp_id = item_values[0]
        role = item_values[2]
        
        if role == "admin":
            return messagebox.showerror("Permission Denied", "System administrators cannot be fired or deleted from the interface.")
            
        if self.emp_repo.delete(emp_id):
            messagebox.showinfo("Success", "Employee removed from database.")
            self.refresh()

    def refresh(self):
        self.emp_tree.delete(*self.emp_tree.get_children())
        for e in self.emp_repo.get_all():
            deduction, net = self.payroll.calculate_current_net_salary(e.id, e.salary)
            self.emp_tree.insert("", "end", values=(e.id, f"{e.first_name} {e.last_name}", e.role, f"${e.salary:,.2f}", f"-${deduction:,.2f}", f"${net:,.2f}"))
        
        self.req_tree.delete(*self.req_tree.get_children())
        for r in self.adv_repo.get_all():
            # Taksit sayısını dinamik olarak hesaplıyoruz
            if r.status == "Approved":
                inst_count = len(self.inst_repo.get_by_advance_id(r.id))
                appr_inst_text = f"{inst_count} Mo"
            else:
                appr_inst_text = "-" # Onaylanmadıysa veya bekliyorsa tire göster

            self.req_tree.insert("", "end", values=(r.id, r.employee_id, f"${r.amount:,.2f}", f"{r.requested_installments} Mo", appr_inst_text, r.reason, r.admin_note, r.status, r.request_date))


class EmployeeDashboard(ttk.Frame):
    def __init__(self, parent, logout_cb):
        super().__init__(parent, padding=20)
        self.logout_cb = logout_cb
        self.user = SessionManager().get_user()
        self.adv_repo, self.inst_repo = AdvanceRepo(), InstallmentRepo()
        self.payroll = PayrollService()
        self.build_ui()

    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 20))
        ttk.Label(header, text=f"Welcome back, {self.user.first_name}!", font=("Helvetica", 18, "bold")).pack(side="left")
        
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side="right")
        ttk.Button(btn_frame, text="Log Out", command=self.logout_cb).pack(side="right")

        self.summary_frame = ttk.LabelFrame(self, text="Salary Projections (Current & Next 2 Months)", padding=15)
        self.summary_frame.pack(fill="x", pady=(0, 20))
        
        self.summary_labels = []
        for i in range(3):
            row_frame = ttk.Frame(self.summary_frame)
            row_frame.pack(fill="x", pady=5)
            
            lbl_month = ttk.Label(row_frame, text="Month", width=12, font=("Helvetica", 12, "bold"))
            lbl_month.pack(side="left")
            
            lbl_base = ttk.Label(row_frame, text="Base: $0.00", width=18, font=("Helvetica", 11))
            lbl_base.pack(side="left")
            
            lbl_deduct = ttk.Label(row_frame, text="Deductions: -$0.00", width=22, font=("Helvetica", 11, "bold"), foreground="red")
            lbl_deduct.pack(side="left")
            
            lbl_net = ttk.Label(row_frame, text="Estimated Net: $0.00", width=25, font=("Helvetica", 12, "bold"), foreground="green")
            lbl_net.pack(side="left")
            
            self.summary_labels.append((lbl_month, lbl_base, lbl_deduct, lbl_net))

        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(action_frame, text="Request New Advance", command=self.request_adv).pack(side="left")
        ttk.Button(action_frame, text="Withdraw Pending Request", command=self.withdraw_request).pack(side="left", padx=(10, 0))
        ttk.Button(action_frame, text="↻ Refresh Status", command=self.refresh).pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.req_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.req_frame, text="Advance Request History")
        
        # YENİ SÜTUN: Appr. Inst.
        req_columns = ("Req ID", "Amount", "Req. Inst.", "Appr. Inst.", "My Reason", "Admin Note", "Status", "Date")
        self.req_tree = ttk.Treeview(self.req_frame, columns=req_columns, show="headings")
        for col in req_columns: self.req_tree.heading(col, text=col)
        self.req_tree.column("Req ID", width=50)
        self.req_tree.column("Req. Inst.", width=70)
        self.req_tree.column("Appr. Inst.", width=70)
        self.req_tree.pack(expand=True, fill="both")

        self.inst_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inst_frame, text="Consolidated Monthly Deductions")
        inst_columns = ("Payment Month (YYYY-MM)", "Total Deduction From Salary", "Status")
        self.inst_tree = ttk.Treeview(self.inst_frame, columns=inst_columns, show="headings")
        for col in inst_columns: self.inst_tree.heading(col, text=col)
        self.inst_tree.pack(expand=True, fill="both")

        self.refresh()

    def request_adv(self):
        AdvanceReqDialog(self)
        self.refresh()

    def withdraw_request(self):
        selected = self.req_tree.selection()
        if not selected:
            return messagebox.showwarning("Warning", "Please select a request to withdraw.")
            
        item_values = self.req_tree.item(selected[0])['values']
        req_id = item_values[0]
        status = item_values[6] # Index kaydı, çünkü araya "Appr. Inst." sütunu eklendi
        
        if status != "Pending":
            return messagebox.showerror("Error", "You can only withdraw requests that are still 'Pending'.")
            
        if messagebox.askyesno("Confirm", "Are you sure you want to withdraw this advance request?"):
            if self.adv_repo.delete(req_id):
                messagebox.showinfo("Success", "Your request has been withdrawn.")
                self.refresh()

    def refresh(self):
        self.req_tree.delete(*self.req_tree.get_children())
        self.inst_tree.delete(*self.inst_tree.get_children())

        projections = self.payroll.get_salary_projections(self.user.id, self.user.salary, num_months=3)
        for i, proj in enumerate(projections):
            lbl_month, lbl_base, lbl_deduct, lbl_net = self.summary_labels[i]
            
            lbl_month.config(text=proj["month_str"])
            lbl_base.config(text=f"Base: ${self.user.salary:,.2f}")
            lbl_deduct.config(text=f"Deductions: -${proj['deduction']:,.2f}")
            lbl_net.config(text=f"Estimated Net: ${proj['net']:,.2f}")

        my_reqs = [r for r in self.adv_repo.get_all() if r.employee_id == self.user.id]
        for r in my_reqs:
            # Taksit sayısını dinamik olarak hesaplıyoruz
            if r.status == "Approved":
                inst_count = len(self.inst_repo.get_by_advance_id(r.id))
                appr_inst_text = f"{inst_count} Mo"
            else:
                appr_inst_text = "-"

            self.req_tree.insert("", "end", values=(r.id, f"${r.amount:,.2f}", f"{r.requested_installments} Mo", appr_inst_text, r.reason, r.admin_note, r.status, r.request_date))
        
        schedule = self.payroll.get_consolidated_schedule(self.user.id)
        for month, total in schedule.items():
            self.inst_tree.insert("", "end", values=(month, f"${total:,.2f}", "Pending / To be Deducted"))