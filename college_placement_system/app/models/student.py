from datetime import datetime, timezone
from app.extensions import db


class Student(db.Model):
    """Student model representing enrolled undergraduate candidates."""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    register_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False)
    cgpa = db.Column(db.Float, nullable=False, default=0.0)
    arrears = db.Column(db.Integer, nullable=False, default=0)
    graduation_year = db.Column(db.Integer, nullable=False, index=True)
    aptitude_score = db.Column(db.Integer, nullable=False, default=0)
    technical_score = db.Column(db.Integer, nullable=False, default=0)
    communication_score = db.Column(db.Integer, nullable=False, default=0)
    internship_experience = db.Column(db.Integer, nullable=False, default=0)
    skills = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    department = db.relationship('Department', back_populates='students')
    placements = db.relationship('Placement', back_populates='student', cascade='all, delete-orphan', lazy='dynamic')
    predictions = db.relationship('Prediction', back_populates='student', cascade='all, delete-orphan', lazy='dynamic')
    eligibilities = db.relationship('Eligibility', back_populates='student', cascade='all, delete-orphan', lazy='dynamic')

    @property
    def is_placed(self):
        """Check if student has been selected in any company."""
        return self.placements.filter_by(status='Selected').first() is not None

    def to_dict(self):
        """Convert model instance to serializable dictionary."""
        return {
            'id': self.id,
            'register_number': self.register_number,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'department_id': self.department_id,
            'department_name': self.department.department_name if self.department else None,
            'department_code': self.department.department_code if self.department else None,
            'cgpa': self.cgpa,
            'arrears': self.arrears,
            'graduation_year': self.graduation_year,
            'aptitude_score': self.aptitude_score,
            'technical_score': self.technical_score,
            'communication_score': self.communication_score,
            'internship_experience': self.internship_experience,
            'skills': self.skills,
            'is_placed': self.is_placed,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f"<Student {self.register_number} - {self.name}>"

