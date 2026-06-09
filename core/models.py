from dataclasses import dataclass
from typing import Optional

class BaseModel:
    pass

@dataclass
class Department(BaseModel):
    name: str
    id: Optional[int] = None

@dataclass
class Employee(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    role: str
    salary: float
    department_id: int
    id: Optional[int] = None

@dataclass
class AdvanceRequest(BaseModel):
    employee_id: int
    amount: float
    requested_installments: int
    reason: str
    status: str
    request_date: str
    admin_note: str = ""
    id: Optional[int] = None

@dataclass
class Installment(BaseModel):
    advance_request_id: int
    amount: float
    due_date: str
    is_paid: bool
    id: Optional[int] = None