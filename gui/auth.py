import tkinter as tk
from tkinter import ttk, messagebox
from core.validators import SessionManager
from database.repositories import EmpRepo
from gui.dashboards import AdminDashboard, EmployeeDashboard

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.emp_repo = EmpRepo()
        self.setup_window()
        self.build_ui()

    def setup_window(self):
        self.title("Login")
        self.geometry("350x250")
        self.eval('tk::PlaceWindow . center')

    def build_ui(self):
        frame = ttk.Frame(self, padding=30)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Sign In", font=("Helvetica", 18, "bold")).pack(pady=(0, 15))

        ttk.Label(frame, text="Email:").pack(anchor="w")
        self.email_entry = ttk.Entry(frame)
        self.email_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Password:").pack(anchor="w")
        self.pass_entry = ttk.Entry(frame, show="*")
        self.pass_entry.pack(fill="x", pady=(0, 15))

        ttk.Button(frame, text="Login", command=self.login).pack(fill="x")

    def login(self):
        email, password = self.email_entry.get(), self.pass_entry.get()
        user = self.emp_repo.get_by_email(email)
        
        if user and user.password == password:
            SessionManager().login(user)
            self.load_dashboard()
        else:
            messagebox.showerror("Authentication Failed", "Invalid email or password.")

    def load_dashboard(self):
        for widget in self.winfo_children(): widget.destroy()
        
        self.geometry("1150x650")
        self.eval('tk::PlaceWindow . center')
        
        user = SessionManager().get_user()
        if user.role == "admin":
            self.title(f"Admin Workspace - {user.first_name} {user.last_name}")
            AdminDashboard(self, self.logout).pack(expand=True, fill="both")
        else:
            self.title(f"Employee Portal - {user.first_name} {user.last_name}")
            EmployeeDashboard(self, self.logout).pack(expand=True, fill="both")

    def logout(self):
        SessionManager().logout()
        for widget in self.winfo_children(): widget.destroy()
        self.setup_window()
        self.build_ui()