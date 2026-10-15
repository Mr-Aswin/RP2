from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS = BASE_DIR / "artifacts"
app = Flask(__name__)

# Load saved artifacts once when the Flask app starts.
def load_artifact(filename):
    path = ARTIFACTS / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Run the notebook artifact-saving cell first."
        )
    return joblib.load(path)

models = {
    "lr_baseline": load_artifact("lr_model.joblib"),
    "rf_baseline": load_artifact("rf_model.joblib"),
    "lr_engineered": load_artifact("lr_fe.joblib"),
    "rf_engineered": load_artifact("rf_fe.joblib"),
}
scalers = {
    "lr_baseline": load_artifact("scaler.joblib"),
    "lr_engineered": load_artifact("scaler_fe.joblib"),
}
with open(ARTIFACTS / "feature_columns.json", "r", encoding="utf-8") as f:
    feature_columns = json.load(f)
with open(ARTIFACTS / "feature_columns_fe.json", "r", encoding="utf-8") as f:
    feature_columns_fe = json.load(f)

RAW_FEATURES = [
    "ambient_temperature_c",
    "supply_air_temperature_c",
    "coolant_temperature_c",
    "humidity_pct",
    "vibration_mm_s",
    "pressure_bar",
    "airflow_m3_h",
    "energy_consumption_kwh",
    "runtime_hours",
    "load_pct",
]
MODEL_OPTIONS = {
    "lr_baseline": "Logistic Regression (baseline)",
    "rf_baseline": "Random Forest (baseline)",
    "lr_engineered": "Logistic Regression (engineered features)",
    "rf_engineered": "Random Forest (engineered features)",
}

DEFAULTS = {
    "ambient_temperature_c": 27.0,
    "supply_air_temperature_c": 18.0,
    "coolant_temperature_c": 44.0,
    "humidity_pct": 55.0,
    "vibration_mm_s": 2.5,
    "pressure_bar": 11.5,
    "airflow_m3_h": 650.0,
    "energy_consumption_kwh": 6.5,
    "runtime_hours": 700.0,
    "load_pct": 65.0,
}

def build_features(raw_values, engineered):
    row = dict(raw_values)
    if engineered:
        row["temperature_difference_c"] = (
            row["ambient_temperature_c"] - row["supply_air_temperature_c"]
        )
        row["energy_per_load"] = (
            row["energy_consumption_kwh"] / max(row["load_pct"], 1.0)
        )
        row["coolant_ambient_difference_c"] = (
            row["coolant_temperature_c"] - row["ambient_temperature_c"]
        )
    return row

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    error = None
    probability = None
    selected_model = "rf_engineered"
    values = DEFAULTS.copy()

    if request.method == "POST":
        selected_model = request.form.get("model", "rf_engineered")
        if selected_model not in MODEL_OPTIONS:
            error = "Please select a valid model."
        else:
            try:
                for feature in RAW_FEATURES:
                    value = float(request.form.get(feature, ""))
                    if not np.isfinite(value):
                        raise ValueError(f"{feature} must be a finite number.")
                    values[feature] = value

                # Basic plausibility validation; adjust limits to match your use case.
                if not 0 <= values["humidity_pct"] <= 100:
                    raise ValueError("Humidity must be between 0 and 100%.")
                if not 0 <= values["load_pct"] <= 100:
                    raise ValueError("Load must be between 0 and 100%.")
                if values["runtime_hours"] < 0:
                    raise ValueError("Runtime hours cannot be negative.")
                if values["vibration_mm_s"] < 0:
                    raise ValueError("Vibration cannot be negative.")
                if values["pressure_bar"] <= 0 or values["airflow_m3_h"] < 0:
                    raise ValueError("Pressure must be positive and airflow cannot be negative.")
                if values["energy_consumption_kwh"] < 0:
                    raise ValueError("Energy consumption cannot be negative.")

                engineered = selected_model.endswith("engineered")
                row = build_features(values, engineered)
                columns = feature_columns_fe if engineered else feature_columns
                X_input = pd.DataFrame([row], columns=columns)

                model = models[selected_model]
                if selected_model.startswith("lr_"):
                    X_input_model = scalers[selected_model].transform(X_input)
                else:
                    X_input_model = X_input.to_numpy()

                pred = int(model.predict(X_input_model)[0])
                probability = float(model.predict_proba(X_input_model)[0, 1])
                prediction = {
                    "label": "Failure likely" if pred == 1 else "Normal",
                    "class": "failure" if pred == 1 else "normal",
                    "probability_pct": round(probability * 100, 2),
                }
            except (ValueError, TypeError) as exc:
                error = str(exc)

    return render_template(
        "index.html",
        raw_features=RAW_FEATURES,
        defaults=values,
        model_options=MODEL_OPTIONS,
        selected_model=selected_model,
        prediction=prediction,
        probability=probability,
        error=error,
    )

if __name__ == "__main__":
    # Local development only. Do not use Flask's debug server in production.
    app.run(host="127.0.0.1", port=5000, debug=True)
