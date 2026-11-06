import numpy as np
import torch

try:
    from app.model_loader import load_model_and_tokenizer
except ImportError:  # pragma: no cover - fallback for direct script execution
    from model_loader import load_model_and_tokenizer


def _normalize_label(raw_label):
    if isinstance(raw_label, str):
        normalized = raw_label.upper()
        if normalized in {"LABEL_0", "NEGATIVE", "0"}:
            return "NEGATIVE"
        if normalized in {"LABEL_1", "POSITIVE", "1"}:
            return "POSITIVE"
        return normalized

    if int(raw_label) == 0:
        return "NEGATIVE"
    if int(raw_label) == 1:
        return "POSITIVE"
    return str(raw_label)


def predict_sentiment(review_text: str):
    cleaned_review = (review_text or "").strip()
    if not cleaned_review:
        raise ValueError("Review text cannot be empty.")

    model, tokenizer, device = load_model_and_tokenizer()

    encoded = tokenizer(
        cleaned_review,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=512,
    )
    encoded = {key: value.to(device) for key, value in encoded.items()}

    with torch.inference_mode():
        logits = model(**encoded).logits

    probabilities = torch.softmax(logits, dim=-1).cpu().numpy()[0]
    np_probabilities = np.asarray(probabilities, dtype=np.float64)

    predicted_index = int(np.argmax(np_probabilities))
    raw_label = model.config.id2label.get(predicted_index, str(predicted_index))
    predicted_label = _normalize_label(raw_label)

    positive_probability = float(np_probabilities[1])
    negative_probability = float(np_probabilities[0])
    confidence = float(np_probabilities[predicted_index])

    return {
        "prediction": predicted_label,
        "confidence": confidence,
        "positive_probability": positive_probability,
        "negative_probability": negative_probability,
        "probabilities": {
            "NEGATIVE": negative_probability,
            "POSITIVE": positive_probability,
        },
        "label_mapping": {
            0: "NEGATIVE",
            1: "POSITIVE",
        },
    }
