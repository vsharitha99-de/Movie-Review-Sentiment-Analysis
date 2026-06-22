import pandas as pd
import pickle
import re
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))  # Load once

def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower()
    words = text.split()
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)

print("Loading dataset...")
df = pd.read_csv("data/IMDB Dataset.csv")
print("Dataset Shape:", df.shape)

df["sentiment"] = df["sentiment"].map({"positive": 1, "negative": 0})
print("Label counts:\n", df["sentiment"].value_counts())

print("Cleaning text... should take ~30 seconds now")
df["clean_review"] = df["review"].apply(clean_text)
print("Cleaning done")

X = df["clean_review"]
y = df["sentiment"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("Applying TF-IDF...")
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

print("Training model...")
model = LogisticRegression(max_iter=1000)
model.fit(X_train_tfidf, y_train)

y_pred = model.predict(X_test_tfidf)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

pickle.dump(model, open("models/sentiment_model.pkl", "wb"))
pickle.dump(tfidf, open("models/tfidf.pkl", "wb"))
print("Model saved in /models/")