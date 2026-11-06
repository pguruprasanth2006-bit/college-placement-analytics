import os
import json
import joblib
import pandas as pd
from datetime import datetime, timezone
from flask import current_app
from app.extensions import db
from app.models import Student, Prediction


class PredictionService:
    """Service managing ML model loading, placement probability inference, and prediction persistence."""

    _model = None
    _metrics = None

    @classmethod
    def load_model(cls):
        """Lazy-load the trained Random Forest model and performance metrics."""
        model_path = current_app.config.get('MODEL_PATH')
        metrics_path = current_app.config.get('MODEL_METRICS_PATH')

        if not os.path.exists(model_path):
            # Attempt to train if not found
            from ml.train_model import train_placement_model
            train_placement_model()

        if cls._model is None and os.path.exists(model_path):
            cls._model = joblib.load(model_path)

        if cls._metrics is None and os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                cls._metrics = json.load(f)

        return cls._model, cls._metrics

    @classmethod
    def get_metrics(cls):
        """Retrieve stored evaluation metrics."""
        _, metrics = cls.load_model()
        return metrics or {}

    @classmethod
    def predict_for_student(cls, student: Student, save_to_db: bool = True) -> dict:
        """
        Run inference for a registered student and optionally save the prediction to MySQL.
        Input features: CGPA, arrears, aptitude_score, technical_score, communication_score, internship_experience.
        """
        model, metrics = cls.load_model()
        if model is None:
            raise RuntimeError("Machine Learning model could not be loaded.")

        # Input feature vector
        feature_dict = {
            'cgpa': float(student.cgpa),
            'arrears': int(student.arrears),
            'aptitude_score': int(student.aptitude_score),
            'technical_score': int(student.technical_score),
            'communication_score': int(student.communication_score),
            'internship_experience': int(student.internship_experience)
        }

        feature_df = pd.DataFrame([feature_dict])

        # Inference
        probability = float(model.predict_proba(feature_df)[0][1])
        prediction_val = int(model.predict(feature_df)[0])
        status = 'Placed' if prediction_val == 1 else 'Not Placed'

        # Persist prediction history
        saved_id = None
        if save_to_db:
            pred_record = Prediction(
                student_id=student.id,
                probability=round(probability, 4),
                predicted_status=status,
                model_version=metrics.get('model_version', '1.0.0') if metrics else '1.0.0',
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(pred_record)
            db.session.commit()
            saved_id = pred_record.id

        return {
            'prediction_id': saved_id,
            'student_id': student.id,
            'student_name': student.name,
            'register_number': student.register_number,
            'department_code': student.department.department_code if student.department else '',
            'features': feature_dict,
            'probability': round(probability, 4),
            'probability_percentage': round(probability * 100, 2),
            'predicted_status': status,
            'model_version': metrics.get('model_version', '1.0.0') if metrics else '1.0.0',
            'model_accuracy': metrics.get('accuracy_percentage', 0.0) if metrics else 0.0
        }

    @classmethod
    def predict_custom_features(cls, features: dict) -> dict:
        """Predict placement probability for arbitrary feature inputs."""
        model, metrics = cls.load_model()
        if model is None:
            raise RuntimeError("Machine Learning model could not be loaded.")

        feature_cols = ['cgpa', 'arrears', 'aptitude_score', 'technical_score', 'communication_score', 'internship_experience']
        clean_features = {col: float(features.get(col, 0)) for col in feature_cols}
        feature_df = pd.DataFrame([clean_features])

        probability = float(model.predict_proba(feature_df)[0][1])
        prediction_val = int(model.predict(feature_df)[0])
        status = 'Placed' if prediction_val == 1 else 'Not Placed'

        return {
            'features': clean_features,
            'probability': round(probability, 4),
            'probability_percentage': round(probability * 100, 2),
            'predicted_status': status,
            'model_version': metrics.get('model_version', '1.0.0') if metrics else '1.0.0'
        }

