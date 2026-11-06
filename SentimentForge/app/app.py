from __future__ import annotations

import os
from typing import Any

import requests
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
CORS(app)

REMOTE_API_URL = os.environ.get("SENTIMENTFORGE_REMOTE_API_URL", "").rstrip("/")
_model_loaded = False

if not REMOTE_API_URL:
    try:
        try:
            from app.model_loader import load_model_and_tokenizer
            from app.predictor import predict_sentiment
        except ImportError:  # pragma: no cover - fallback for direct script execution
            from model_loader import load_model_and_tokenizer
            from predictor import predict_sentiment

        load_model_and_tokenizer()
        _model_loaded = True
    except Exception:
        app.logger.exception("Failed to load the SentimentForge model.")


@app.errorhandler(RequestEntityTooLarge)
def handle_request_too_large(_error: RequestEntityTooLarge):
    return jsonify(
        {
            "error": "Request body must not exceed 1 MiB.",
            "status": _error.code,
        }
    ), 413


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


def _request_remote(
    method: str,
    endpoint: str,
    payload: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, int]:
    try:
        response = requests.request(
            method,
            f"{REMOTE_API_URL}{endpoint}",
            json=payload,
            timeout=(5, 50),
        )
    except requests.RequestException:
        app.logger.exception("The configured SentimentForge inference service is unavailable.")
        return {"error": "The inference service is unavailable."}, 502

    try:
        response_data = response.json()
    except ValueError:
        app.logger.error("The configured inference service returned invalid JSON.")
        return {"error": "The inference service returned an invalid response."}, 502

    if not isinstance(response_data, dict):
        app.logger.error("The configured inference service returned a non-object JSON response.")
        return {"error": "The inference service returned an invalid response."}, 502

    return response_data, response.status_code


@app.route("/health", methods=["GET"])
def health():
    if REMOTE_API_URL:
        response_data, upstream_status = _request_remote("GET", "/health")
        if response_data is None or upstream_status >= 500:
            return jsonify(
                {
                    "status": "error",
                    "model_loaded": False,
                    "error": "The inference service is unavailable.",
                }
            ), 503

        model_loaded = response_data.get("model_loaded") is True
        status = "ok" if response_data.get("status") == "ok" and model_loaded else "error"
        return jsonify({"status": status, "model_loaded": model_loaded}), (
            200 if status == "ok" else 503
        )

    if not _model_loaded:
        return jsonify(
            {
                "status": "error",
                "model_loaded": False,
                "error": "The model could not be loaded; check the server logs.",
            }
        ), 503

    return jsonify({"status": "ok", "model_loaded": True})


@app.route("/predict", methods=["POST"])
def predict():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json."}), 400

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    review = payload.get("review")
    if not isinstance(review, str):
        return jsonify({"error": "'review' must be a string."}), 400
    if not review.strip():
        return jsonify({"error": "'review' must not be empty."}), 400

    if REMOTE_API_URL:
        response_data, upstream_status = _request_remote(
            "POST",
            "/predict",
            {"review": review},
        )
        if response_data is None:
            return jsonify({"error": "The inference service returned an invalid response."}), 502
        return jsonify(response_data), upstream_status

    if not _model_loaded:
        return jsonify(
            {
                "error": "The model is unavailable; check the server logs.",
            }
        ), 503

    try:
        result = predict_sentiment(review)
    except Exception:
        app.logger.exception("Sentiment prediction failed.")
        return jsonify({"error": "Unable to generate a sentiment prediction."}), 500

    sentiment = "Positive" if result["prediction"] == "POSITIVE" else "Negative"
    return jsonify(
        {
            "sentiment": sentiment,
            "confidence": result["confidence"],
            "positive_probability": result["positive_probability"],
            "negative_probability": result["negative_probability"],
        }
    )


if __name__ == "__main__":
    app.run(debug=False)
