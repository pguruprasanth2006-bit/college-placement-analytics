from app.models.department import Department
from app.models.company import Company, company_departments
from app.models.student import Student
from app.models.placement import Placement
from app.models.prediction import Prediction
from app.models.eligibility import Eligibility
from app.models.user import AdminUser

__all__ = [
    'Department',
    'Company',
    'company_departments',
    'Student',
    'Placement',
    'Prediction',
    'Eligibility',
    'AdminUser'
]
