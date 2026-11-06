import os
import json
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'sample_placement_data.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'saved_model', 'placement_model.joblib')
METRICS_PATH = os.path.join(BASE_DIR, 'ml', 'saved_model', 'model_metrics.json')

FEATURE_COLUMNS = [
    'cgpa',
    'arrears',
    'aptitude_score',
    'technical_score',
    'communication_score',
    'internship_experience'
]


def evaluate_existing_model(model_path=None, data_path=None):
    """Load the trained model and output detailed classification and feature report."""
    if model_path is None:
        model_path = MODEL_PATH
    if data_path is None:
        data_path = DATA_PATH

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found at {model_path}. Run train_model.py first.")

    model = joblib.load(model_path)
    df = pd.read_csv(data_path)

    clean_df = df[FEATURE_COLUMNS + ['placement_status']].dropna().copy()
    clean_df['target'] = clean_df['placement_status'].apply(
        lambda x: 1 if str(x).strip().lower() in ('placed', 'selected', '1', 'true') else 0
    )

    X = clean_df[FEATURE_COLUMNS]
    y = clean_df['target']

    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]

    report = classification_report(y, y_pred, target_names=['Not Placed', 'Placed'], output_dict=True)
    cm = confusion_matrix(y, y_pred).tolist()
    auc = float(roc_auc_score(y, y_prob))

    print("================ MODEL EVALUATION REPORT ================")
    print(classification_report(y, y_pred, target_names=['Not Placed', 'Placed']))
    print(f"ROC-AUC Score: {auc:.4f}")
    print(f"Confusion Matrix: {cm}")

    result = {
        'classification_report': report,
        'confusion_matrix': cm,
        'roc_auc': round(auc, 4),
        'total_evaluated_samples': len(X)
    }

    return result


if __name__ == '__main__':
    evaluate_existing_model()

