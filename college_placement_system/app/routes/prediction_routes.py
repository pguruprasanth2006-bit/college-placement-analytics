from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.auth import login_required
from app.models import Student, Prediction
from app.services.prediction_service import PredictionService

prediction_bp = Blueprint('prediction', __name__)


@prediction_bp.route('/', methods=['GET'])
@login_required
def index():
    """Display placement prediction interface, student selector, and model evaluation metrics."""
    students = Student.query.order_by(Student.name.asc()).all()
    selected_student_id = request.args.get('student_id', type=int)

    result = None
    selected_student = None

    if selected_student_id:
        selected_student = db.session.get(Student, selected_student_id)
        if selected_student:
            try:
                result = PredictionService.predict_for_student(selected_student, save_to_db=True)
            except Exception as e:
                flash(f"Prediction error: {str(e)}", 'danger')

    metrics = PredictionService.get_metrics()
    recent_predictions = Prediction.query.order_by(Prediction.id.desc()).limit(10).all()

    return render_template(
        'prediction.html',
        students=students,
        selected_student=selected_student,
        result=result,
        metrics=metrics,
        recent_predictions=recent_predictions
    )


@prediction_bp.route('/custom', methods=['POST'])
@login_required
def predict_custom():
    """Predict placement likelihood for manual feature inputs."""
    cgpa = request.form.get('cgpa', type=float)
    arrears = request.form.get('arrears', 0, type=int)
    aptitude = request.form.get('aptitude_score', 0, type=int)
    technical = request.form.get('technical_score', 0, type=int)
    communication = request.form.get('communication_score', 0, type=int)
    internship = request.form.get('internship_experience', 0, type=int)

    if cgpa is None or cgpa < 0 or cgpa > 10:
        flash("CGPA must be between 0.0 and 10.0.", "danger")
        return redirect(url_for('prediction.index'))

    features = {
        'cgpa': cgpa,
        'arrears': arrears,
        'aptitude_score': aptitude,
        'technical_score': technical,
        'communication_score': communication,
        'internship_experience': internship
    }

    try:
        custom_result = PredictionService.predict_custom_features(features)
        students = Student.query.order_by(Student.name.asc()).all()
        metrics = PredictionService.get_metrics()
        recent_predictions = Prediction.query.order_by(Prediction.id.desc()).limit(10).all()

        return render_template(
            'prediction.html',
            students=students,
            selected_student=None,
            result=custom_result,
            metrics=metrics,
            recent_predictions=recent_predictions,
            custom_input=features
        )
    except Exception as e:
        flash(f"Inference error: {str(e)}", "danger")
        return redirect(url_for('prediction.index'))

