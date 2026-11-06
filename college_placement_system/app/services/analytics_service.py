import pandas as pd
import numpy as np
from sqlalchemy import select
from app.extensions import db
from app.models import Student, Company, Placement, Department


class AnalyticsService:
    """Service providing statistical and business intelligence analytics using Pandas and NumPy."""

    @staticmethod
    def get_placement_dataframe():
        """
        Extract active placement records and student profiles directly from the database
        into a clean, normalized Pandas DataFrame.
        """
        # Query joined data: Student + Department + Placement (if any) + Company (if any)
        query = (
            db.session.query(
                Student.id.label('student_id'),
                Student.register_number,
                Student.name,
                Student.cgpa,
                Student.arrears,
                Student.graduation_year,
                Student.aptitude_score,
                Student.technical_score,
                Student.communication_score,
                Student.internship_experience,
                Department.department_name,
                Department.department_code,
                Placement.status.label('placement_status'),
                Placement.salary,
                Placement.placement_date,
                Company.company_name
            )
            .join(Department, Student.department_id == Department.id)
            .outerjoin(Placement, Student.id == Placement.student_id)
            .outerjoin(Company, Placement.company_id == Company.id)
        )

        rows = query.all()
        if not rows:
            # Return empty DataFrame with defined columns
            return pd.DataFrame(columns=[
                'student_id', 'register_number', 'name', 'cgpa', 'arrears', 'graduation_year',
                'aptitude_score', 'technical_score', 'communication_score', 'internship_experience',
                'department_name', 'department_code', 'placement_status', 'salary', 'placement_date', 'company_name',
                'is_placed'
            ])

        # Convert SQLAlchemy Row objects to list of dicts
        data = [r._asdict() for r in rows]
        df = pd.DataFrame(data)

        # Clean duplicates: if a student has multiple placement records, prioritize 'Selected'
        df['is_placed'] = df['placement_status'].apply(lambda x: 1 if str(x).strip() == 'Selected' else 0)
        df = df.sort_values(by=['student_id', 'is_placed', 'salary'], ascending=[True, False, False])
        df = df.drop_duplicates(subset=['student_id'], keep='first').copy()

        # Handle missing values
        df['salary'] = df['salary'].fillna(0.0).astype(float)
        df['company_name'] = df['company_name'].fillna('Unplaced')
        df['placement_status'] = df['placement_status'].fillna('Not Placed')
        df['cgpa'] = pd.to_numeric(df['cgpa'], errors='coerce').fillna(0.0)
        df['arrears'] = pd.to_numeric(df['arrears'], errors='coerce').fillna(0).astype(int)
        df['graduation_year'] = pd.to_numeric(df['graduation_year'], errors='coerce').fillna(2025).astype(int)

        return df

    @classmethod
    def generate_summary_metrics(cls, df=None):
        """Calculate high-level KPI metrics safely with NumPy."""
        if df is None:
            df = cls.get_placement_dataframe()

        total_students = int(len(df))
        if total_students == 0:
            return {
                'total_students': 0,
                'total_placed': 0,
                'total_unplaced': 0,
                'placement_percentage': 0.0,
                'average_package': 0.0,
                'median_package': 0.0,
                'highest_package': 0.0,
                'minimum_package': 0.0
            }

        placed_mask = df['is_placed'] == 1
        placed_df = df[placed_mask]
        total_placed = int(np.sum(placed_mask))
        total_unplaced = int(total_students - total_placed)

        placement_percentage = float(np.round((total_placed / total_students) * 100.0, 2)) if total_students > 0 else 0.0

        if total_placed > 0 and len(placed_df['salary']) > 0:
            salaries = placed_df['salary'].to_numpy()
            avg_pkg = float(np.round(np.mean(salaries), 2))
            med_pkg = float(np.round(np.median(salaries), 2))
            max_pkg = float(np.round(np.max(salaries), 2))
            min_pkg = float(np.round(np.min(salaries[salaries > 0]) if np.any(salaries > 0) else 0.0, 2))
        else:
            avg_pkg = 0.0
            med_pkg = 0.0
            max_pkg = 0.0
            min_pkg = 0.0

        return {
            'total_students': total_students,
            'total_placed': total_placed,
            'total_unplaced': total_unplaced,
            'placement_percentage': placement_percentage,
            'average_package': avg_pkg,
            'median_package': med_pkg,
            'highest_package': max_pkg,
            'minimum_package': min_pkg
        }

    @classmethod
    def department_wise_analytics(cls, df=None):
        """Generate department-level breakdown of student registrations, selections, and rates."""
        if df is None:
            df = cls.get_placement_dataframe()

        if df.empty:
            return []

        dept_groups = df.groupby(['department_name', 'department_code'])
        results = []

        for (dept_name, dept_code), group in dept_groups:
            total = len(group)
            placed = int(group['is_placed'].sum())
            unplaced = total - placed
            rate = float(np.round((placed / total) * 100.0, 2)) if total > 0 else 0.0

            salaries = group[group['is_placed'] == 1]['salary'].to_numpy()
            avg_sal = float(np.round(np.mean(salaries), 2)) if len(salaries) > 0 else 0.0
            max_sal = float(np.round(np.max(salaries), 2)) if len(salaries) > 0 else 0.0

            results.append({
                'department_name': dept_name,
                'department_code': dept_code,
                'total_students': total,
                'placed_students': placed,
                'unplaced_students': unplaced,
                'placement_percentage': rate,
                'average_salary': avg_sal,
                'highest_salary': max_sal
            })

        return sorted(results, key=lambda x: x['placement_percentage'], reverse=True)

    @classmethod
    def company_wise_analytics(cls, df=None):
        """Calculate placement counts and average packages grouped by company."""
        if df is None:
            df = cls.get_placement_dataframe()

        placed_df = df[df['is_placed'] == 1]
        if placed_df.empty:
            return []

        grouped = placed_df.groupby('company_name')
        results = []

        for company_name, group in grouped:
            if company_name == 'Unplaced':
                continue
            count = len(group)
            salaries = group['salary'].to_numpy()
            avg_pkg = float(np.round(np.mean(salaries), 2)) if len(salaries) > 0 else 0.0
            max_pkg = float(np.round(np.max(salaries), 2)) if len(salaries) > 0 else 0.0

            results.append({
                'company_name': company_name,
                'placed_count': int(count),
                'average_package': avg_pkg,
                'highest_package': max_pkg
            })

        return sorted(results, key=lambda x: x['placed_count'], reverse=True)

    @classmethod
    def year_wise_analytics(cls, df=None):
        """Analyze year-on-year placement trends."""
        if df is None:
            df = cls.get_placement_dataframe()

        if df.empty:
            return []

        grouped = df.groupby('graduation_year')
        results = []

        for year, group in grouped:
            total = len(group)
            placed = int(group['is_placed'].sum())
            rate = float(np.round((placed / total) * 100.0, 2)) if total > 0 else 0.0
            salaries = group[group['is_placed'] == 1]['salary'].to_numpy()
            avg_pkg = float(np.round(np.mean(salaries), 2)) if len(salaries) > 0 else 0.0

            results.append({
                'year': int(year),
                'total_students': total,
                'placed_students': placed,
                'placement_percentage': rate,
                'average_package': avg_pkg
            })

        return sorted(results, key=lambda x: x['year'])

    @classmethod
    def cgpa_vs_placement_analytics(cls, df=None):
        """Analyze correlation between CGPA tiers and placement success rates."""
        if df is None:
            df = cls.get_placement_dataframe()

        if df.empty:
            return []

        bins = [0.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        labels = ['< 6.0', '6.0 - 6.99', '7.0 - 7.99', '8.0 - 8.99', '9.0 - 10.0']

        df_copy = df.copy()
        df_copy['cgpa_tier'] = pd.cut(df_copy['cgpa'], bins=bins, labels=labels, right=False)

        results = []
        for tier in labels:
            group = df_copy[df_copy['cgpa_tier'] == tier]
            total = len(group)
            placed = int(group['is_placed'].sum()) if total > 0 else 0
            rate = float(np.round((placed / total) * 100.0, 2)) if total > 0 else 0.0
            results.append({
                'tier': tier,
                'total_students': total,
                'placed_students': placed,
                'placement_percentage': rate
            })

        return results

