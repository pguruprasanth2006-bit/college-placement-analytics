from datetime import datetime, timezone
from app.extensions import db


class Placement(db.Model):
    """Placement model recording application, interview and selection outcomes."""
    __tablename__ = 'placements'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    placement_date = db.Column(db.Date, nullable=True)
    status = db.Column(
        db.String(50),
        nullable=False,
        default='Applied'
    )  # Applied, Shortlisted, Selected, Rejected, Not Placed
    salary = db.Column(db.Float, nullable=False, default=0.0)  # Package in LPA
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Constraint to prevent duplicate records for same student and company
    __table_args__ = (
        db.UniqueConstraint('student_id', 'company_id', name='uq_student_company_placement'),
    )

    # Relationships
    student = db.relationship('Student', back_populates='placements')
    company = db.relationship('Company', back_populates='placements')

    def to_dict(self):
        """Convert model instance to serializable dictionary."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'register_number': self.student.register_number if self.student else None,
            'department_name': self.student.department.department_name if (self.student and self.student.department) else None,
            'company_id': self.company_id,
            'company_name': self.company.company_name if self.company else None,
            'job_role': self.company.job_role if self.company else None,
            'placement_date': self.placement_date.strftime('%Y-%m-%d') if self.placement_date else None,
            'status': self.status,
            'salary': self.salary,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f"<Placement Student:{self.student_id} Company:{self.company_id} Status:{self.status}>"

