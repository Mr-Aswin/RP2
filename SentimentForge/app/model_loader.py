from functools import lru_cache
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "distilbert_finetuned"


@lru_cache(maxsize=1)
def load_model_and_tokenizer():
    if not MODEL_DIR.exists():
        raise FileNotFoundError(
            f"Missing model directory: {MODEL_DIR}. "
            "Ensure the fine-tuned DistilBERT model is present in models/distilbert_finetuned/."
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
    model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
    model.to(device)
    model.eval()
    return model, tokenizer, device
