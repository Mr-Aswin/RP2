# SentimentForge – Sentiment Analysis Using Deep Learning

<p align="center">
  <strong>An NLP-based movie review sentiment classification system powered by Machine Learning, Recurrent Neural Networks, and Transformers.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-Deep%20Learning-ee4c2c?logo=pytorch" alt="PyTorch">
  <img src="https://img.shields.io/badge/Hugging%20Face-DistilBERT-yellow?logo=huggingface" alt="Hugging Face">
  <img src="https://img.shields.io/badge/Streamlit-Web%20Application-ff4b4b?logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/Task-Binary%20Classification-success" alt="Binary Classification">
</p>

---

## Overview

**SentimentForge** is a deep learning-based Natural Language Processing (NLP) project that analyzes movie reviews and classifies them into two sentiment categories: Positive and Negative.

The project explores multiple approaches to text representation and sentiment classification, ranging from traditional machine learning techniques to recurrent neural networks and transformer-based architectures.

The primary objective is to investigate the trade-offs between predictive performance, model complexity, storage requirements, and inference efficiency.

The project also includes an interactive Streamlit application that allows users to submit movie reviews and receive real-time sentiment predictions with confidence scores.

## Objectives

- Perform exploratory data analysis on textual review data.
- Develop a systematic text preprocessing pipeline.
- Explore TF-IDF-based text representation.
- Implement and compare multiple recurrent neural network architectures.
- Fine-tune a pretrained DistilBERT transformer model.
- Evaluate models using standard classification metrics.
- Analyze model errors and per-class performance.
- Compare models based on accuracy, size, and inference speed.
- Develop an interactive sentiment prediction application.

## Dataset

**IMDb Movie Reviews Dataset – 50K Reviews**

- Source: [IMDb Dataset on Kaggle](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews)
- Total reviews: 50,000
- Features:
  - `review`: Movie review text.
  - `sentiment`: Sentiment label.
- Classes:
  - Positive
  - Negative
- Distribution: 25,000 positive and 25,000 negative reviews.

The dataset is balanced, containing an equal number of positive and negative reviews.

## Project Workflow

The project follows a structured NLP and deep learning workflow.

1. Dataset exploration and analysis.
2. Text cleaning and preprocessing.
3. Feature extraction and tokenization.
4. Classical machine learning experiments.
5. Recurrent neural network development.
6. Transformer fine-tuning.
7. Model evaluation and error analysis.
8. Model benchmarking.
9. Interactive application development.

## Exploratory Data Analysis

The dataset exploration included:

- Dataset structure and data quality inspection.
- Class distribution analysis.
- Duplicate review identification.
- Review character and word-length distributions.
- Word cloud visualization.
- Most frequent word analysis.
- N-gram analysis.
- Text length analysis to understand sequence truncation requirements.

### Dataset observations

| Metric | Result |
|---|---:|
| Total reviews | 50,000 |
| Positive reviews | 25,000 |
| Negative reviews | 25,000 |
| Duplicate reviews | 418 |
| Average review length | 231.16 words |
| Median review length | 173 words |

## Text Preprocessing

A dedicated preprocessing pipeline was developed for the recurrent and TF-IDF models.

The preprocessing steps included:

- HTML tag removal.
- Lowercasing.
- URL removal.
- Special character cleaning.
- Whitespace normalization.
- Tokenization.
- Sequence padding and truncation.

Stopwords were intentionally retained to preserve sentiment-related negations such as *not*, *never*, and *don't*.

### Data splitting

The dataset was divided using stratified sampling:

| Dataset | Samples |
|---|---:|
| Training | 40,000 |
| Validation | 5,000 |
| Testing | 5,000 |
| Total | 50,000 |

A maximum vocabulary size of 30,000 and a sequence length of 300 were used for the recurrent neural network experiments.

**Note:** DistilBERT uses its own Hugging Face tokenizer and receives raw review text, with a maximum sequence length of 512 tokens.

## Models Implemented

The project compares traditional machine learning, recurrent neural networks, and transformer-based deep learning.

### 1. Classical Machine Learning

**TF-IDF + Logistic Regression**

- TF-IDF feature extraction.
- Unigram and bigram representation.
- Maximum features: 50,000.
- Logistic Regression classifier.

**TF-IDF + Multinomial Naive Bayes**

- TF-IDF feature extraction.
- Multinomial Naive Bayes classification.
- Used as an additional classical baseline.

### 2. Recurrent Neural Networks

The following sequence models were implemented using PyTorch:

| Model | Architecture |
|---|---|
| Simple RNN | Recurrent Neural Network |
| LSTM | Long Short-Term Memory |
| BiLSTM | Bidirectional LSTM |
| GRU | Gated Recurrent Unit |

The recurrent models use learned embedding layers to convert token IDs into dense vector representations.

The experiments explore sequence modelling, embedding dimensions, hidden representations, and training performance.

### 3. Transformer Model

**Fine-tuned DistilBERT**

- Base model: `distilbert-base-uncased`
- Framework: Hugging Face Transformers and PyTorch.
- Maximum sequence length: 512.
- Fine-tuning epochs: 3.
- Optimizer: AdamW.
- Learning rate: 2e-5.
- Weight decay: 0.01.
- Learning rate scheduling with warmup and linear decay.
- Mixed-precision training.

The best checkpoint was selected based on validation loss, corresponding to epoch 2.

## Model Evaluation

All evaluated models were tested on the same 5,000-sample stratified test split.

The following evaluation metrics were used:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC

### Final Test Results

| Model | Accuracy | Precision | Recall | F1-score | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| **DistilBERT** | **94.12%** | 93.80% | **94.48%** | **94.14%** | **98.51%** |
| Logistic Regression | 91.22% | 91.47% | 90.92% | 91.19% | 97.15% |
| GRU | 88.84% | 89.03% | 88.60% | 88.81% | 95.71% |
| Naive Bayes | 88.14% | 88.71% | 87.40% | 88.05% | 95.39% |
| BiLSTM | 84.64% | 88.76% | 79.32% | 83.78% | 92.30% |
| LSTM | 70.56% | 75.96% | 60.16% | 67.14% | 73.92% |

**Best-performing model:** Fine-tuned DistilBERT, with 94.12% test accuracy.

The Simple RNN was also implemented and trained, but a saved checkpoint and final test evaluation were not available. It is therefore excluded from the final test comparison.

## Model Benchmarking

The models were also compared based on storage size, inference latency, and throughput.

### Benchmark Results

| Model | Accuracy | Model Size | Latency / Review | Throughput / Second |
|---|---:|---:|---:|---:|
| Logistic Regression | 91.22% | 2.05 MB | 0.56 ms | 1,782.04 |
| GRU | 88.84% | 15.03 MB | 4.08 ms | 244.94 |
| DistilBERT | 94.12% | 256.10 MB | 1,128.26 ms | 0.89 |

### Benchmark Observations

**DistilBERT**
- Highest predictive accuracy.
- Largest model size.
- Highest measured inference latency.

**Logistic Regression**
- Smallest model size.
- Lowest measured inference latency.
- Highest measured throughput.
- Competitive classification performance.

**GRU**
- Intermediate model size and inference speed.
- Better accuracy than the evaluated LSTM and BiLSTM models.

### Overall Comparison

DistilBERT provides the strongest predictive performance, whereas Logistic Regression offers the most efficient solution in terms of model size and measured inference speed.

GRU provides another alternative between the two approaches.

*Benchmark latency and throughput represent the measurements from the experimental environment and are dependent on hardware, batch size, and implementation details. They should not be interpreted as universal performance guarantees.*

## Visualizations and Error Analysis

The evaluation workflow includes:

- Class distribution visualization.
- Review length distributions.
- Word clouds.
- Frequent word and n-gram visualizations.
- Training and validation performance analysis.
- Confusion matrices.
- ROC curve comparison.
- Per-class precision, recall, and F1-score.
- GRU misclassification analysis.

The error analysis examines false positives and false negatives to understand cases where the model incorrectly classifies a review.

## Interactive Web Application

SentimentForge includes a Streamlit application connected to the fine-tuned DistilBERT model.

### Application Features

- Text input for movie reviews.
- Positive and negative sentiment classification.
- Prediction confidence.
- Positive probability.
- Negative probability.
- Visual probability comparison.
- Model information.
- Example reviews.
- Input character and word counts.

The application runs inference locally using the saved model and tokenizer.

### Application Preview

The application provides a dark-themed interface designed to make sentiment predictions and probability scores easy to understand.

### Run the Application

```bash
streamlit run app/app.py
```

The fine-tuned DistilBERT model must be available locally in:

```text
models/distilbert_finetuned/
```

## Project Structure

```text
SentimentForge/
│
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── components.py
│   ├── model_loader.py
│   ├── predictor.py
│   └── styles.py
│
├── data/
│   └── raw/
│       └── IMDB Dataset.csv
│
├── models/
│   ├── distilbert_finetuned/
│   ├── bilstm_model.pth
│   ├── distilbert_best.pth
│   ├── gru_epoch5_last.pth
│   ├── logistic_regression.pkl
│   ├── lstm_model.pth
│   ├── preprocessing_config.json
│   ├── tfidf_vectorizer.pkl
│   └── tokenizer.pkl
│
├── notebooks/
│   ├── 01_dataset_exploration.ipynb
│   ├── 02_text_preprocessing.ipynb
│   ├── 03_tfidf_baseline.ipynb
│   ├── 04_rnn_lstm_models.ipynb
│   ├── 05_bilstm_gru_experiments.ipynb
│   ├── 06_transformer_finetuning.ipynb
│   ├── 07_model_evaluation.ipynb
│   └── 08_model_benchmarking.ipynb
│
├── reports/
│   ├── bilstm_experiment.json
│   ├── distilbert_experiment.json
│   ├── distilbert_test_predictions.npz
│   ├── experiment_results.csv
│   ├── final_model_comparison.csv
│   ├── gru_error_analysis.csv
│   ├── gru_experiment.json
│   ├── lstm_experiment.json
│   ├── model_benchmark_comparison.csv
│   ├── per_class_performance.csv
│   ├── recurrent_model_comparison.csv
│   └── roc_curve_comparison.png
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation and Setup

### 1. Clone the RP2 repository

```bash
git lfs install
git clone https://github.com/Mr-Aswin/RP2.git
cd "RP2/SentimentForge"
git lfs pull
```

The dataset and model checkpoints are stored with Git LFS. Install Git LFS before cloning, then run `git lfs pull` if the large files were not downloaded automatically.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare the model

The fine-tuned DistilBERT model is included at:

```text
models/distilbert_finetuned/
```

The directory contains the model weights, configuration, and tokenizer files. The dataset and other saved model checkpoints are also included in this project folder.

### 5. Run SentimentForge

```bash
streamlit run app/app.py
```

The application will open in your default browser.

## Limitations

- The project focuses on binary sentiment classification.
- The dataset consists of IMDb movie reviews, so performance on unrelated text domains may differ.
- Sarcasm, irony, mixed opinions, and context-dependent expressions can be challenging.
- Prediction confidence represents the model's estimated probability and does not guarantee correctness.
- DistilBERT has higher storage and computational requirements than the classical machine learning baseline.
- Inference performance depends on the hardware and execution environment.

## Future Improvements

- Explore pretrained Word2Vec, GloVe, or FastText representations.
- Experiment with dropout and additional regularization in recurrent architectures.
- Investigate model quantization and other inference optimizations.
- Improve robustness on mixed sentiment, sarcasm, and domain-specific text.
- Explore additional datasets beyond movie reviews.
- Evaluate deployment options for wider accessibility.

## Conclusion

SentimentForge demonstrates a comparative approach to binary sentiment analysis using traditional machine learning, recurrent neural networks, and transformer-based architectures.

Through systematic experimentation, the project shows that model selection involves balancing predictive performance with computational efficiency.

Fine-tuned DistilBERT achieved the highest test accuracy of 94.12%, while Logistic Regression delivered the smallest model size and fastest measured inference. GRU offered an intermediate alternative.

The project brings together data exploration, preprocessing, deep learning experimentation, evaluation, benchmarking, and an interactive application into a complete NLP workflow.

---

## Acknowledgements

- IMDb Movie Reviews Dataset – [Kaggle](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews)
- Hugging Face – [Transformers](https://huggingface.co/docs/transformers/index)
- PyTorch – [Official Documentation](https://pytorch.org/docs/stable/index.html)
- Streamlit – [Official Documentation](https://docs.streamlit.io/)

---

<p align="center">
  <strong>SentimentForge</strong><br>
  Exploring the intersection of Natural Language Processing and Deep Learning.
</p>