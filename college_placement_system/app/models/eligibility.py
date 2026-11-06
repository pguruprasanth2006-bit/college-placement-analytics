from datetime import datetime, timezone
from app.extensions import db


class Eligibility(db.Model):
    """Eligibility check result mapping student qualifications against company criteria."""
    __tablename__ = 'eligibilities'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    is_eligible = db.Column(db.Boolean, nullable=False, default=False)
    rejection_reason = db.Column(db.String(255), nullable=True)
    checked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    student = db.relationship('Student', back_populates='eligibilities')
    company = db.relationship('Company', back_populates='eligibilities')

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
            'is_eligible': self.is_eligible,
            'rejection_reason': self.rejection_reason,
            'checked_at': self.checked_at.strftime('%Y-%m-%d %H:%M:%S') if self.checked_at else None
        }

    def __repr__(self):
        return f"<Eligibility Student:{self.student_id} Company:{self.company_id} Eligible:{self.is_eligible}>"

