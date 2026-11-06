from datetime import datetime, timezone
from app.extensions import db

# Association Table for Many-to-Many Relationship between Company and Department
company_departments = db.Table(
    'company_departments',
    db.Column('company_id', db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), primary_key=True),
    db.Column('department_id', db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), primary_key=True)
)


class Company(db.Model):
    """Company model representing recruiters and criteria."""
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False, index=True)
    job_role = db.Column(db.String(100), nullable=False)
    minimum_cgpa = db.Column(db.Float, nullable=False, default=6.0)
    maximum_arrears = db.Column(db.Integer, nullable=False, default=0)
    package = db.Column(db.Float, nullable=False, default=0.0)  # Package in LPA (Lakhs Per Annum)
    graduation_year = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Many-to-Many with Department
    eligible_departments = db.relationship(
        'Department',
        secondary=company_departments,
        back_populates='companies'
    )

    # One-to-Many with Placements and Eligibility checks
    placements = db.relationship('Placement', back_populates='company', cascade='all, delete-orphan', lazy='dynamic')
    eligibilities = db.relationship('Eligibility', back_populates='company', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        """Convert model instance to serializable dictionary."""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'job_role': self.job_role,
            'minimum_cgpa': self.minimum_cgpa,
            'maximum_arrears': self.maximum_arrears,
            'package': self.package,
            'graduation_year': self.graduation_year,
            'eligible_departments': [
                {'id': dept.id, 'name': dept.department_name, 'code': dept.department_code}
                for dept in self.eligible_departments
            ],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f"<Company {self.company_name} - {self.job_role}>"

