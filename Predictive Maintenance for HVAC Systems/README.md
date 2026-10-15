# 🛠️ HVAC Predictive Maintenance

### 🤖 Machine Learning--Powered HVAC Failure Prediction with Flask

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20App-black?logo=flask&logoColor=white)
![scikit--learn](https://img.shields.io/badge/scikit--learn-ML-orange?logo=scikitlearn&logoColor=white)
![Status](https://img.shields.io/badge/Status-Educational%20Project-informational)

Predict potential HVAC equipment failures from sensor readings using
machine learning. This project compares **Logistic Regression** and
**Random Forest** models and provides a simple **Flask web interface**
where users can enter sensor values and switch between trained models.

> ⚠️ **Disclaimer:** This project uses a synthetic dataset for
> educational purposes. Predictions are not validated for real HVAC
> equipment and must not be used as the sole basis for maintenance or
> safety decisions.

------------------------------------------------------------------------

## 📌 Table of Contents

-   [✨ Features](#-features)
-   [🧠 Models](#-models)
-   [📊 Dataset](#-dataset)
-   [🏆 Baseline Results](#-baseline-results)
-   [🧰 Tech Stack](#-tech-stack)
-   [📁 Project Structure](#-project-structure)
-   [⚙️ Setup and Installation](#️-setup-and-installation)
-   [💾 Export Trained Models](#-export-trained-models)
-   [🚀 Run the Flask App](#-run-the-flask-app)
-   [🖥️ App Preview](#️-app-preview)
-   [🔬 Workflow](#-workflow)
-   [🛣️ Future Improvements](#️-future-improvements)
-   [🤝 Contributing](#-contributing)
-   [📄 License](#-license)

## ✨ Features

-   📥 Accepts HVAC sensor readings through a web form.
-   🔀 Switch between four saved model variants:
    -   Logistic Regression --- baseline
    -   Random Forest --- baseline
    -   Logistic Regression --- engineered features
    -   Random Forest --- engineered features
-   🧹 Uses median imputation during preprocessing.
-   📏 Scales inputs for Logistic Regression; Random Forest uses
    unscaled inputs.
-   🧪 Displays a predicted class and model-estimated failure
    probability.
-   📊 Supports evaluation using accuracy, precision, recall, F1-score,
    ROC-AUC, confusion matrices, and feature importance.
-   🧩 Includes derived features for the engineered models.

## 🧠 Models

### 1. Logistic Regression

A linear classification baseline. Standardized sensor features are used
to help optimization and regularization.

### 2. Random Forest

An ensemble of decision trees that can learn nonlinear relationships.
Feature scaling is not generally required.

### 3. Engineered-feature variants

The engineered models use the original ten sensor features plus:

-   `temperature_difference_c` --- ambient temperature minus supply-air
    temperature.
-   `energy_per_load` --- energy consumption divided by load percentage
    (with a lower bound on the denominator).
-   `coolant_ambient_difference_c` --- coolant temperature minus ambient
    temperature.

These derived features are experimental and are not guaranteed to
improve predictive performance.

## 📊 Dataset

The project uses a **synthetic dataset with 15,000 rows and 14
columns**.

Example sensor fields include:

  Feature                      Description
  ---------------------------- -------------------------------------------
  `ambient_temperature_c`      Ambient temperature in °C
  `supply_air_temperature_c`   Supply-air temperature in °C
  `coolant_temperature_c`      Coolant temperature in °C
  `humidity_pct`               Relative humidity percentage
  `vibration_mm_s`             Vibration measurement
  `pressure_bar`               Operating pressure in bar
  `airflow_m3_h`               Airflow rate
  `energy_consumption_kwh`     Energy consumption
  `runtime_hours`              Runtime hours
  `load_pct`                   Equipment load percentage
  `failure`                    Target label: `0` = normal, `1` = failure

The dataset includes missing sensor values and some extreme readings to
practice data preprocessing. Sensor observations were generated
independently rather than as continuous histories for each machine, so
the dataset is useful for learning the ML workflow but does not
establish real-world predictive validity.

## 🏆 Baseline Results

Results from the current chronological test split:

  -----------------------------------------------------------------------------
  Model            Accuracy    Precision       Recall     F1-score      ROC-AUC
  ------------ ------------ ------------ ------------ ------------ ------------
  Logistic           0.8020       0.2679       0.7888       0.4000       0.8588
  Regression                                                       
  --- baseline                                                     

  Random             0.8857       0.3789       0.5737       0.4564       0.8479
  Forest ---                                                       
  baseline                                                         

  Logistic           0.8020       0.2673       0.7849       0.3988       0.8591
  Regression                                                       
  ---                                                              
  engineered                                                       

  Random             0.8877       0.3856       0.5777       0.4625       0.8527
  Forest ---                                                       
  engineered                                                       
  -----------------------------------------------------------------------------

**Current observation:** Random Forest with engineered features has the
highest F1-score in these experiments, while Logistic Regression has
higher failure recall. The appropriate model depends on the cost of
missed failures versus false alerts.

These scores are from a single test split on synthetic data; they should
not be interpreted as real-world performance guarantees.

## 🧰 Tech Stack

-   **Language:** Python
-   **Data processing:** Pandas, NumPy
-   **Machine learning:** scikit-learn
-   **Model persistence:** Joblib
-   **Web framework:** Flask
-   **Frontend:** HTML, CSS, Jinja templates
-   **Visualization:** Matplotlib, Seaborn

## 📁 Project Structure

``` text
hvac-predictive-maintenance/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── artifacts/
    ├── lr_model.joblib
    ├── rf_model.joblib
    ├── lr_fe.joblib
    ├── rf_fe.joblib
    ├── scaler.joblib
    ├── scaler_fe.joblib
    ├── feature_columns.json
    └── feature_columns_fe.json
```

The `artifacts/` directory must contain the models and preprocessing
artifacts exported from your training notebook. Model files are not
included in this README.

## ⚙️ Setup and Installation

### 1. Clone your repository

``` bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Replace the URL with your actual GitHub repository URL.

### 2. Create a virtual environment

**Windows (PowerShell):**

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

## 💾 Export Trained Models

After training the four models and two scalers in your notebook, save
the artifacts:

``` python
import os
import json
import joblib

os.makedirs("artifacts", exist_ok=True)

joblib.dump(lr_model, "artifacts/lr_model.joblib")
joblib.dump(rf_model, "artifacts/rf_model.joblib")
joblib.dump(lr_fe, "artifacts/lr_fe.joblib")
joblib.dump(rf_fe, "artifacts/rf_fe.joblib")

joblib.dump(scaler, "artifacts/scaler.joblib")
joblib.dump(scaler_fe, "artifacts/scaler_fe.joblib")

with open("artifacts/feature_columns.json", "w", encoding="utf-8") as f:
    json.dump(X_train.columns.tolist(), f)

with open("artifacts/feature_columns_fe.json", "w", encoding="utf-8") as f:
    json.dump(X_train_fe.columns.tolist(), f)
```

Ensure the saved feature names and their order match the columns used
when each model was trained. Only load model artifacts that you created
or trust, since loading Joblib/pickle files can execute code.

## 🚀 Run the Flask App

Once `artifacts/` is in place:

``` bash
python app.py
```

Open the following URL in your browser:

**http://127.0.0.1:5000**

Select a model, enter the sensor readings, and click **Predict failure
risk**.

> 🔐 The included Flask development server is intended for local
> development only. Do not expose it publicly with debug mode enabled.
> For production, use a suitable WSGI server and configure deployment
> security.

## 🖥️ App Preview

Add screenshots of your own running application to a `screenshots/`
folder, then uncomment and update these examples:

``` markdown
![HVAC app dashboard](screenshots/dashboard.png)
![HVAC prediction result](screenshots/prediction-result.png)
```

You can also add a workflow diagram or model evaluation charts, such as
the confusion matrix and ROC curve, to make the repository easier to
understand.

## 🔬 Workflow

1.  Load the synthetic HVAC dataset.
2.  Explore and clean the data.
3.  Split chronologically into training and test sets.
4.  Fit the median imputer on training features and transform test
    features with the same imputer.
5.  Inspect potential outliers; avoid automatically removing genuine
    failure signals.
6.  Scale features for Logistic Regression.
7.  Train and evaluate Logistic Regression and Random Forest.
8.  Create engineered features and compare the results.
9.  Export trained models and preprocessing artifacts.
10. Load the artifacts in Flask and run predictions from form inputs.

## 🛣️ Future Improvements

-   [ ] Tune the classification threshold using a validation set.
-   [ ] Add precision-recall curves and calibration checks.
-   [ ] Add permutation importance on validation data.
-   [ ] Validate on realistic, time-ordered HVAC equipment histories.
-   [ ] Add automated tests for input validation and prediction routes.
-   [ ] Improve accessibility and mobile layout.
-   [ ] Deploy using a production-ready WSGI server.
-   [ ] Add monitoring for data drift and model performance.

## 🤝 Contributing

Suggestions and improvements are welcome:

1.  Fork the repository.
2.  Create a feature branch.
3.  Make your changes and test them.
4.  Open a pull request describing the improvement.

## 📄 License

Choose a license before publishing this repository. For example, you may
use the MIT License by adding a `LICENSE` file, provided that it matches
your intended project terms.

------------------------------------------------------------------------

⭐ If you find this project useful for learning predictive maintenance
and machine learning, consider starring the repository!
