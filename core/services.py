from datetime import date
from database.repositories import AdvanceRepo, InstallmentRepo

class PayrollService:
    def __init__(self):
        self.adv_repo = AdvanceRepo()
        self.inst_repo = InstallmentRepo()

    def calculate_current_net_salary(self, emp_id: int, base_salary: float) -> tuple[float, float]:
        today = date.today()
        current_month_str = f"{today.year}-{today.month:02d}"
        advances = [adv for adv in self.adv_repo.get_all() if adv.employee_id == emp_id and adv.status == "Approved"]
        
        total_deduction = 0.0
        for adv in advances:
            for inst in self.inst_repo.get_by_advance_id(adv.id):
                if inst.due_date.startswith(current_month_str) and not inst.is_paid:
                    total_deduction += inst.amount

        net_salary = base_salary - total_deduction
        return round(total_deduction, 2), round(net_salary, 2)

    def get_salary_projections(self, emp_id: int, base_salary: float, num_months: int = 3) -> list[dict]:
        today = date.today()
        projections = []
        
        advances = [adv for adv in self.adv_repo.get_all() if adv.employee_id == emp_id and adv.status == "Approved"]
        installments = []
        for adv in advances:
            installments.extend(self.inst_repo.get_by_advance_id(adv.id))

        for i in range(num_months):
            month = today.month - 1 + i
            year = today.year + month // 12
            month = month % 12 + 1
            month_str = f"{year}-{month:02d}"
            
            deduction = sum(inst.amount for inst in installments if inst.due_date.startswith(month_str) and not inst.is_paid)
            net = base_salary - deduction
            
            projections.append({
                "month_str": month_str,
                "deduction": round(deduction, 2),
                "net": round(net, 2)
            })
            
        return projections

    def get_consolidated_schedule(self, emp_id: int) -> dict:
        schedule = {}
        advances = [adv for adv in self.adv_repo.get_all() if adv.employee_id == emp_id and adv.status == "Approved"]
        
        for adv in advances:
            for inst in self.inst_repo.get_by_advance_id(adv.id):
                if not inst.is_paid:
                    month_key = inst.due_date[:7]
                    schedule[month_key] = schedule.get(month_key, 0.0) + inst.amount
                    
        return dict(sorted(schedule.items()))