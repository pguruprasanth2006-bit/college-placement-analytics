import os
import sys
import pandas as pd
from datetime import datetime, date

# Add parent directory to path so imports work cleanly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import Department, Company, Student, Placement, AdminUser


def seed_database(app=None):
    """Seed the database with initial departments, companies, students, placements, and admin."""
    if app is None:
        app = create_app(os.getenv('FLASK_ENV', 'development'))

    with app.app_context():
        # Ensure all tables exist
        db.create_all()

        print("Checking admin user...")
        admin = AdminUser.query.filter_by(username=app.config.get('ADMIN_USERNAME', 'admin')).first()
        if not admin:
            admin = AdminUser(username=app.config.get('ADMIN_USERNAME', 'admin'))
            admin.set_password(app.config.get('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)
            print(f"Created default admin user: {admin.username}")

        print("Seeding departments...")
        dept_data = [
            {'department_name': 'Computer Science and Engineering', 'department_code': 'CSE'},
            {'department_name': 'Information Technology', 'department_code': 'IT'},
            {'department_name': 'Electronics and Communication Engineering', 'department_code': 'ECE'},
            {'department_name': 'Electrical and Electronics Engineering', 'department_code': 'EEE'},
            {'department_name': 'Mechanical Engineering', 'department_code': 'MECH'}
        ]

        dept_map = {}
        for d in dept_data:
            dept = Department.query.filter_by(department_code=d['department_code']).first()
            if not dept:
                dept = Department(department_name=d['department_name'], department_code=d['department_code'])
                db.session.add(dept)
                db.session.flush()
            dept_map[d['department_name']] = dept
            dept_map[d['department_code']] = dept

        print("Seeding recruiting companies...")
        company_data = [
            {
                'company_name': 'Google',
                'job_role': 'Software Engineer',
                'minimum_cgpa': 8.5,
                'maximum_arrears': 0,
                'package': 22.0,
                'graduation_year': 2025,
                'depts': ['CSE', 'IT', 'ECE']
            },
            {
                'company_name': 'Amazon',
                'job_role': 'SDE-1',
                'minimum_cgpa': 8.0,
                'maximum_arrears': 0,
                'package': 18.5,
                'graduation_year': 2025,
                'depts': ['CSE', 'IT']
            },
            {
                'company_name': 'Microsoft',
                'job_role': 'Cloud Engineer',
                'minimum_cgpa': 8.0,
                'maximum_arrears': 0,
                'package': 19.0,
                'graduation_year': 2025,
                'depts': ['CSE', 'IT', 'ECE']
            },
            {
                'company_name': 'Zoho',
                'job_role': 'Member Technical Staff',
                'minimum_cgpa': 7.0,
                'maximum_arrears': 1,
                'package': 8.5,
                'graduation_year': 2025,
                'depts': ['CSE', 'IT', 'ECE', 'EEE', 'MECH']
            },
            {
                'company_name': 'TCS',
                'job_role': 'Systems Engineer',
                'minimum_cgpa': 6.0,
                'maximum_arrears': 1,
                'package': 3.8,
                'graduation_year': 2025,
                'depts': ['CSE', 'IT', 'ECE', 'EEE', 'MECH']
            },
            {
                'company_name': 'Infosys',
                'job_role': 'Specialist Programmer',
                'minimum_cgpa': 6.5,
                'maximum_arrears': 1,
                'package': 4.5,
                'graduation_year': 2025,
                'depts': ['CSE', 'IT', 'ECE', 'EEE']
            },
            {
                'company_name': 'Cognizant',
                'job_role': 'Programmer Analyst',
                'minimum_cgpa': 6.5,
                'maximum_arrears': 1,
                'package': 4.2,
                'graduation_year': 2025,
                'depts': ['CSE', 'IT', 'ECE', 'EEE', 'MECH']
            },
            {
                'company_name': 'Accenture',
                'job_role': 'Associate Software Engineer',
                'minimum_cgpa': 6.5,
                'maximum_arrears': 1,
                'package': 4.5,
                'graduation_year': 2025,
                'depts': ['CSE', 'IT', 'ECE', 'EEE', 'MECH']
            }
        ]

        company_map = {}
        for c in company_data:
            comp = Company.query.filter_by(company_name=c['company_name'], job_role=c['job_role']).first()
            if not comp:
                comp = Company(
                    company_name=c['company_name'],
                    job_role=c['job_role'],
                    minimum_cgpa=c['minimum_cgpa'],
                    maximum_arrears=c['maximum_arrears'],
                    package=c['package'],
                    graduation_year=c['graduation_year']
                )
                for dept_code in c['depts']:
                    if dept_code in dept_map:
                        comp.eligible_departments.append(dept_map[dept_code])
                db.session.add(comp)
                db.session.flush()
            company_map[c['company_name']] = comp

        db.session.commit()

        # Seed students from sample CSV
        csv_path = app.config.get('DATA_PATH')
        if csv_path and os.path.exists(csv_path):
            print(f"Loading students from {csv_path}...")
            df = pd.read_csv(csv_path)

            students_added = 0
            placements_added = 0

            for _, row in df.iterrows():
                reg_no = str(row['register_number']).strip()
                email = str(row['email']).strip()

                student = Student.query.filter_by(register_number=reg_no).first()
                if not student:
                    dept_name = str(row['department']).strip()
                    dept = dept_map.get(dept_name) or Department.query.filter_by(department_name=dept_name).first()
                    if not dept:
                        continue

                    student = Student(
                        register_number=reg_no,
                        name=str(row['name']).strip(),
                        email=email,
                        phone=str(row['phone']).strip() if pd.notna(row['phone']) else None,
                        department_id=dept.id,
                        cgpa=float(row['cgpa']),
                        arrears=int(row['arrears']),
                        graduation_year=int(row['graduation_year']),
                        aptitude_score=int(row['aptitude_score']),
                        technical_score=int(row['technical_score']),
                        communication_score=int(row['communication_score']),
                        internship_experience=int(row['internship_experience']),
                        skills=str(row['skills']).strip() if pd.notna(row['skills']) else ''
                    )
                    db.session.add(student)
                    db.session.flush()
                    students_added += 1

                # If student is placed and company is in company_map, add placement record
                if str(row.get('placement_status', '')).strip() == 'Placed':
                    comp_name = str(row.get('company_name', '')).strip()
                    comp = company_map.get(comp_name)
                    if comp:
                        existing_placement = Placement.query.filter_by(
                            student_id=student.id,
                            company_id=comp.id
                        ).first()
                        if not existing_placement:
                            placed_date = None
                            if pd.notna(row.get('placement_date')) and str(row.get('placement_date')).strip():
                                try:
                                    placed_date = datetime.strptime(str(row['placement_date']).strip(), '%Y-%m-%d').date()
                                except ValueError:
                                    placed_date = date.today()

                            salary = float(row.get('salary', comp.package)) if pd.notna(row.get('salary')) else comp.package
                            placement = Placement(
                                student_id=student.id,
                                company_id=comp.id,
                                placement_date=placed_date,
                                status='Selected',
                                salary=salary
                            )
                            db.session.add(placement)
                            placements_added += 1

            db.session.commit()
            print(f"Seeding completed: Added {students_added} students and {placements_added} placements.")
        else:
            print(f"Sample data file not found at {csv_path}, skipped student seeding.")

        print("Database initialized and seeded successfully.")


if __name__ == '__main__':
    seed_database()

