# HVAC Predictive Maintenance — Flask demo

This starter app lets you switch between four trained models:
- Logistic Regression baseline
- Random Forest baseline
- Logistic Regression with engineered features
- Random Forest with engineered features

The app expects model/scaler artifacts exported from your own notebook. The ZIP does not include trained model binaries because those objects exist in your notebook runtime.

## 1. Save artifacts from your notebook

Run the artifact-saving code provided in the ChatGPT conversation after you have trained:
`lr_model`, `rf_model`, `lr_fe`, `rf_fe`, `scaler`, `scaler_fe`, `X_train`, and `X_train_fe`.

It creates the `artifacts/` folder with the required `.joblib` and `.json` files.

## 2. Install dependencies

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## 3. Run the app

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Notes
- This is a local educational demo, not a production maintenance system.
- The synthetic dataset's observations are independently generated; predictions are not validated for real HVAC equipment.
- The app validates a few basic physical input limits. Update them for your equipment and sensor specifications.
- Do not expose Flask's debug server to the public internet.
