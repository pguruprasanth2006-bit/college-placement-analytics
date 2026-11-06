from datetime import datetime, timezone
from app.extensions import db
from app.models import Student, Company, Eligibility


class EligibilityService:
    """Core eligibility engine evaluating student qualifications against recruitment criteria."""

    @staticmethod
    def evaluate_student(student: Student, company: Company) -> tuple[bool, list[str]]:
        """
        Evaluate a single student against a company's recruitment criteria.
        Returns (is_eligible, list_of_rejection_reasons).
        """
        reasons = []

        # 1. CGPA Check
        if student.cgpa < company.minimum_cgpa:
            reasons.append(f"CGPA {student.cgpa:.2f} is below minimum requirement of {company.minimum_cgpa:.2f}")

        # 2. Arrears Check
        if student.arrears > company.maximum_arrears:
            reasons.append(f"Standing arrears ({student.arrears}) exceeds maximum allowed ({company.maximum_arrears})")

        # 3. Department Check
        eligible_dept_ids = [d.id for d in company.eligible_departments]
        if eligible_dept_ids and student.department_id not in eligible_dept_ids:
            dept_codes = ", ".join([d.department_code for d in company.eligible_departments])
            student_code = student.department.department_code if student.department else 'Unknown'
            reasons.append(f"Department '{student_code}' is not among eligible disciplines ({dept_codes})")

        # 4. Graduation Year Check
        if student.graduation_year != company.graduation_year:
            reasons.append(f"Graduation year {student.graduation_year} does not match drive year ({company.graduation_year})")

        is_eligible = len(reasons) == 0
        return is_eligible, reasons

    @classmethod
    def check_and_record(cls, student_id: int, company_id: int) -> dict:
        """Evaluate and persist the eligibility result to the database."""
        student = db.session.get(Student, student_id)
        company = db.session.get(Company, company_id)

        if not student or not company:
            return {'error': 'Student or Company not found'}

        is_eligible, reasons = cls.evaluate_student(student, company)
        reason_str = "; ".join(reasons) if reasons else "Meets all criteria"

        # Record or update in database
        record = Eligibility.query.filter_by(student_id=student.id, company_id=company.id).first()
        if not record:
            record = Eligibility(
                student_id=student.id,
                company_id=company.id,
                is_eligible=is_eligible,
                rejection_reason=reason_str,
                checked_at=datetime.now(timezone.utc)
            )
            db.session.add(record)
        else:
            record.is_eligible = is_eligible
            record.rejection_reason = reason_str
            record.checked_at = datetime.now(timezone.utc)

        db.session.commit()

        return {
            'student_id': student.id,
            'student_name': student.name,
            'register_number': student.register_number,
            'company_id': company.id,
            'company_name': company.company_name,
            'is_eligible': is_eligible,
            'rejection_reasons': reasons,
            'reason_summary': reason_str
        }

    @classmethod
    def evaluate_company_pool(cls, company_id: int) -> dict:
        """
        Evaluate all registered students for a specific company recruitment drive.
        Categorizes students into eligible and ineligible lists with reasons.
        """
        company = db.session.get(Company, company_id)
        if not company:
            return {'error': 'Company not found', 'eligible': [], 'ineligible': []}

        # Query all students
        students = Student.query.all()
        eligible_list = []
        ineligible_list = []

        for student in students:
            is_eligible, reasons = cls.evaluate_student(student, company)
            data = {
                'student_id': student.id,
                'name': student.name,
                'register_number': student.register_number,
                'department_code': student.department.department_code if student.department else '',
                'cgpa': student.cgpa,
                'arrears': student.arrears,
                'graduation_year': student.graduation_year,
                'reasons': reasons
            }
            if is_eligible:
                eligible_list.append(data)
            else:
                ineligible_list.append(data)

        return {
            'company': company,
            'eligible': eligible_list,
            'ineligible': ineligible_list,
            'total_evaluated': len(students),
            'eligible_count': len(eligible_list),
            'ineligible_count': len(ineligible_list)
        }

