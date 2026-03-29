#!/usr/bin/env python3
"""
CWSI Stress Prediction Model - Standalone Script
Professional implementation of CWSI regression with automatic stress classification
"""

# Core data science libraries
import pandas as pd
import numpy as np

# Machine learning libraries
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Model persistence
import joblib
import warnings
warnings.filterwarnings('ignore')

def classify_stress_level(cwsi_percentage):
    """
    Classify crop water stress level based on CWSI percentage.

    Parameters:
    cwsi_percentage (float): CWSI value as percentage (0-100)

    Returns:
    str: Stress level classification
    
    Thresholds:
    - low: 0-24.4%
    - mild: 24.4-49.7%
    - medium: 49.7-60%
    - high: 60-82%
    - extreme: 82-100%
    """
    if cwsi_percentage <= 24.4:
        return 'low'
    elif cwsi_percentage <= 49.7:
        return 'mild'
    elif cwsi_percentage < 60:
        return 'medium'
    elif cwsi_percentage <= 82:
        return 'high'
    else:  # cwsi_percentage > 82
        return 'extreme'

def main():
    print(" CWSI Stress Prediction Model")
    print("=" * 50)

    # Load dataset
    print(" Loading dataset...")
    df = pd.read_csv('salsabil_dataset_2000.csv')
    print(f"   • Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")

    # Feature selection
    EXCLUDED_COLUMNS = ['id', 'date', 'year', 'stress_label', 'cwsi']
    FEATURE_COLUMNS = [col for col in df.columns if col not in EXCLUDED_COLUMNS]

    # Identify categorical columns
    categorical_columns = ['region', 'soil_type', 'crop_type']

    # Encode categorical variables
    df_processed = df.copy()
    label_encoders = {}

    print(" Encoding categorical variables...")
    for col in categorical_columns:
        encoder = LabelEncoder()
        df_processed[col] = encoder.fit_transform(df_processed[col])
        label_encoders[col] = encoder

    # Prepare feature matrix and target vector
    X = df_processed[FEATURE_COLUMNS].values
    y = df_processed['cwsi'].values

    # Train-test split (keep indices)
    X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(
        X, y, np.arange(len(df)), test_size=0.2, random_state=42
    )

    # Model training
    print(" Training Random Forest Regressor...")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    print(" Model training completed")

    # Model evaluation
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    print("\n Model Performance Metrics:")
    print("=" * 50)
    print(f"  Mean Absolute Error (MAE): {mae:.4f}")
    print(f"  Root Mean Squared Error (RMSE): {rmse:.4f}")
    print(f"  R² Score: {r2:.4f}")
    print(f"  Mean Squared Error (MSE): {mse:.4f}")

    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2', n_jobs=-1)
    print(f"  Cross-Validation R² (Mean ± Std): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Test stress classification
    print("\n Testing Stress Classification:")
    y_pred_percentage = y_pred * 100
    predicted_stress_levels = [classify_stress_level(pct) for pct in y_pred_percentage]
    actual_stress_levels = df.iloc[indices_test]['stress_label'].values

    correct_predictions = sum(1 for pred, actual in zip(predicted_stress_levels, actual_stress_levels) if pred == actual)
    classification_accuracy = correct_predictions / len(predicted_stress_levels) * 100

    print(f"  Classification Accuracy: {classification_accuracy:.2f}%")

    # Save model
    print("\n Saving model...")
    joblib.dump(model, 'cwsi_regression_model.pkl')
    joblib.dump(label_encoders, 'categorical_encoders.pkl')

    model_info = {
        'features': FEATURE_COLUMNS,
        'categorical_columns': categorical_columns,
        'performance_metrics': {
            'mae': mae, 'rmse': rmse, 'r2': r2,
            'cv_r2_mean': cv_scores.mean(),
            'classification_accuracy': classification_accuracy
        }
    }
    joblib.dump(model_info, 'model_metadata.pkl')

    print(" Model saved successfully!")
    print("   • cwsi_regression_model.pkl")
    print("   • categorical_encoders.pkl")
    print("   • model_metadata.pkl")

    # Example prediction
    print("\n Example Prediction:")
    sample_data = {
        'region': 'Kairouan', 'latitude': 35.67, 'longitude': 10.10,
        'soil_type': 'clay-loam', 'crop_type': 'Wheat', 'month': 7,
        'lst_celsius': 38.5, 'ndvi': 0.32, 'savi': 0.28, 'evi': 0.25,
        'ta_celsius': 34.0, 'rh_percent': 28.0, 'wind_ms': 3.2,
        'solar_wm2': 820.0, 'vpd_kpa': 3.8, 'et0_mm_day': 7.5,
        'soil_moisture': 0.11, 'field_capacity': 0.28,
        'wilting_point': 0.10, 'irrigation_event': 0
    }

    # Prepare sample for prediction
    sample = sample_data.copy()
    for col in categorical_columns:
        sample[col] = label_encoders[col].transform([sample[col]])[0]

    feature_vector = np.array([[sample[feature] for feature in FEATURE_COLUMNS]])
    cwsi_prediction = model.predict(feature_vector)[0]
    cwsi_percentage = cwsi_prediction * 100
    stress_level = classify_stress_level(cwsi_percentage)

    print(f"  Predicted CWSI: {cwsi_percentage:.1f}%")
    print(f" Stress Level: {stress_level.upper()}")

if __name__ == "__main__":
    main()