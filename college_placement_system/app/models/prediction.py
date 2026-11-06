from datetime import datetime, timezone
from app.extensions import db


class Prediction(db.Model):
    """Prediction model storing ML-generated placement likelihoods."""
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    probability = db.Column(db.Float, nullable=False)  # Between 0.0 and 1.0 (or percentage 0-100)
    predicted_status = db.Column(db.String(50), nullable=False)  # 'Placed' or 'Not Placed'
    model_version = db.Column(db.String(50), nullable=False, default='1.0.0')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    student = db.relationship('Student', back_populates='predictions')

    def to_dict(self):
        """Convert model instance to serializable dictionary."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'register_number': self.student.register_number if self.student else None,
            'department_name': self.student.department.department_name if (self.student and self.student.department) else None,
            'probability': round(self.probability, 4),
            'probability_percentage': round(self.probability * 100, 2),
            'predicted_status': self.predicted_status,
            'model_version': self.model_version,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f"<Prediction Student:{self.student_id} Status:{self.predicted_status} Prob:{self.probability}>"

