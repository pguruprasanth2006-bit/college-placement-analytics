import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'sample_placement_data.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'ml', 'saved_model')
MODEL_PATH = os.path.join(MODEL_DIR, 'placement_model.joblib')
METRICS_PATH = os.path.join(MODEL_DIR, 'model_metrics.json')

FEATURE_COLUMNS = [
    'cgpa',
    'arrears',
    'aptitude_score',
    'technical_score',
    'communication_score',
    'internship_experience'
]
TARGET_COLUMN = 'placement_status'


def train_placement_model(csv_path=None, test_size=0.2, random_state=42):
    """
    Train a Random Forest Classifier on historical placement data.
    Evaluates model performance and saves the model artifact and metrics.
    """
    if csv_path is None:
        csv_path = DATA_PATH

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Training dataset not found at {csv_path}")

    print(f"Loading placement training data from: {csv_path}")
    df = pd.read_csv(csv_path)

    # Validate required columns
    missing_cols = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing required columns: {missing_cols}")

    # Data Cleaning and Preparation
    clean_df = df[FEATURE_COLUMNS + [TARGET_COLUMN]].dropna().copy()

    # Encode Target: Placed -> 1, Not Placed -> 0
    clean_df['target'] = clean_df[TARGET_COLUMN].apply(
        lambda x: 1 if str(x).strip().lower() in ('placed', 'selected', '1', 'true') else 0
    )

    class_counts = clean_df['target'].value_counts().to_dict()
    print(f"Target distribution: {class_counts}")

    if len(class_counts) < 2:
        raise ValueError("Dataset lacks representation of both outcome classes (Placed and Not Placed). Reliable training impossible.")

    if len(clean_df) < 20:
        raise ValueError(f"Dataset too small ({len(clean_df)} rows). Reliable model training requires larger dataset.")

    X = clean_df[FEATURE_COLUMNS]
    y = clean_df['target']

    # Train-test split with fixed random seed for reproducibility
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Initialize and train Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=random_state
    )
    rf_model.fit(X_train, y_train)

    # Model Evaluation
    y_pred = rf_model.predict(X_test)
    y_prob = rf_model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Calculate feature importances
    importances = dict(zip(FEATURE_COLUMNS, [float(round(imp, 4)) for imp in rf_model.feature_importances_]))

    metrics = {
        'model_name': 'Random Forest Classifier',
        'model_version': '1.0.0',
        'n_estimators': 100,
        'features': FEATURE_COLUMNS,
        'feature_importances': importances,
        'training_samples': int(len(X_train)),
        'test_samples': int(len(X_test)),
        'accuracy': round(acc, 4),
        'accuracy_percentage': round(acc * 100, 2),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'confusion_matrix': cm,
        'trained_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Ensure model directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Save model and metrics
    joblib.dump(rf_model, MODEL_PATH)
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=4)

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")
    print(f"Performance: Accuracy={acc:.4f}, Precision={prec:.4f}, Recall={rec:.4f}, F1={f1:.4f}")

    return rf_model, metrics


if __name__ == '__main__':
    train_placement_model()

