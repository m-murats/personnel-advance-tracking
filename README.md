# Personnel Advance Tracking System 💼

A comprehensive, desktop-based Human Resources and Finance application built entirely with Python. This system digitalizes the process of requesting, reviewing, and tracking employee salary advances with a strict Role-Based Access Control (RBAC) mechanism.

## 🚀 Features

### 👨‍💼 Admin Workspace
* **Personnel Management:** Securely add, update, or remove employees.
* **Request Review:** Evaluate pending advance requests with options to approve, reject, and override installment plans.
* **Company Overview:** Real-time dashboard of all employees, base salaries, monthly deductions, and net payouts.

### 🧑‍💻 Employee Workspace
* **Advance Requests:** Submit precise advance requests including reasoning and preferred monthly installments.
* **Financial Tracking:** Detailed history of all past and pending requests, along with admin feedback.
* **Salary Projections:** Dynamic 3-month financial projection calculating consolidated active debts and estimated net payouts.

## 🛠️ Architecture & Technologies
This project requires **zero external dependencies** and is built strictly using Python Standard Libraries.
* **Language:** Python 3.x
* **GUI:** `tkinter` and `ttk` module (Modern layered interface)
* **Database:** `sqlite3` (Relational DB with strict Foreign Key constraints)
* **Design Pattern:** Layered Architecture (Core/Models, Database/Repositories, GUI/Views) & OOP (22 modular classes)

## ⚙️ Usage

To run this application locally, simply execute the main entry point:

`python main.py`

*(Note: The SQLite database and tables will automatically initialize on the first run. The system comes with built-in RBAC features).*
