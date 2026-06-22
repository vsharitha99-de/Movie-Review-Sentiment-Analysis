# 🎬 Movie Review Sentiment Analysis

## 📌 Project Overview

Movie Review Sentiment Analysis is a Natural Language Processing (NLP) and Machine Learning project that classifies movie reviews as **Positive** or **Negative** based on the text provided by the user.

The project uses text preprocessing, TF-IDF feature extraction, and a trained **Logistic Regression** model to analyze review sentiments and provide real-time predictions through an interactive Streamlit web application.

---

## 🚀 Features

* Predicts sentiment of movie reviews as Positive or Negative
* Real-time review analysis
* Text preprocessing and cleaning
* TF-IDF feature extraction
* Interactive Streamlit web interface
* Machine Learning-based sentiment classification

---

## 🛠️ Technologies Used

* Python
* Pandas
* NumPy
* NLTK
* Scikit-learn
* TF-IDF Vectorizer
* Streamlit
* Pickle

---

## 📂 Project Structure

```text
Movie-Review-Sentiment-Analysis/
│
├── data/
│   └── IMDB Dataset.csv
│
├── models/
│   ├── sentiment_model.pkl
│   └── tfidf.pkl
│
├── Bulk_Review_Analyzer.py
├── train_model.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ How It Works

1. User enters a movie review.
2. The review text is cleaned and preprocessed.
3. TF-IDF converts the text into numerical features.
4. The trained Logistic Regression model predicts the sentiment.
5. The result is displayed as Positive or Negative.

---

## 📊 Results

The model successfully classifies movie reviews using NLP preprocessing and TF-IDF feature extraction. The application provides real-time sentiment predictions through a simple and user-friendly Streamlit interface.

---

## 🎯 Learning Outcomes

* Text preprocessing using NLP techniques
* Feature extraction using TF-IDF
* Machine Learning model training and evaluation
* Model serialization using Pickle
* Streamlit application development
* End-to-end machine learning workflow implementation

---


