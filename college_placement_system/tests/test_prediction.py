import pytest
import os
from app.models import Student, Prediction
from app.services.prediction_service import PredictionService
from ml.train_model import train_placement_model


def test_model_training(tmp_path):
    """Test that model training runs successfully and creates metrics."""
    model, metrics = train_placement_model()
    assert model is not None
    assert 'accuracy' in metrics
    assert metrics['accuracy'] > 0.60
    assert 'confusion_matrix' in metrics
    assert 'feature_importances' in metrics


def test_model_prediction_for_student(db, seed_basic_data):
    """Test generating a placement prediction for a student and saving to DB."""
    alice = seed_basic_data['student_alice']

    result = PredictionService.predict_for_student(alice, save_to_db=True)
    assert 'probability' in result
    assert 0.0 <= result['probability'] <= 1.0
    assert result['predicted_status'] in ('Placed', 'Not Placed')

    # Verify saved in Prediction table
    saved = Prediction.query.filter_by(student_id=alice.id).first()
    assert saved is not None
    assert saved.predicted_status == result['predicted_status']
    assert round(saved.probability, 4) == result['probability']


def test_predict_custom_features(app):
    """Test predicting for arbitrary feature vector."""
    with app.app_context():
        # High performing student
        high_features = {
            'cgpa': 9.5,
            'arrears': 0,
            'aptitude_score': 95,
            'technical_score': 98,
            'communication_score': 92,
            'internship_experience': 2
        }
        high_result = PredictionService.predict_custom_features(high_features)
        assert high_result['probability'] > 0.5

        # Poor performing student
        low_features = {
            'cgpa': 5.2,
            'arrears': 4,
            'aptitude_score': 40,
            'technical_score': 35,
            'communication_score': 42,
            'internship_experience': 0
        }
        low_result = PredictionService.predict_custom_features(low_features)
        assert low_result['probability'] < high_result['probability']

