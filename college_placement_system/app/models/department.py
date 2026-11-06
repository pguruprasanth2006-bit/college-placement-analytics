from datetime import datetime, timezone
from app.extensions import db


class Department(db.Model):
    """Department model representing academic disciplines in the college."""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    department_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    students = db.relationship('Student', back_populates='department', cascade='all, delete-orphan', lazy='dynamic')
    companies = db.relationship(
        'Company',
        secondary='company_departments',
        back_populates='eligible_departments'
    )

    def to_dict(self):
        """Convert model instance to serializable dictionary."""
        return {
            'id': self.id,
            'department_name': self.department_name,
            'department_code': self.department_code,
            'student_count': self.students.count() if hasattr(self.students, 'count') else 0
        }

    def __repr__(self):
        return f"<Department {self.department_code} - {self.department_name}>"

