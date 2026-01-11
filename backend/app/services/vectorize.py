from sklearn.feature_extraction.text import TfidfVectorizer
from app.services.preprocess import preprocess_text

class Vectorizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def fit(self, texts: list[str]):
        processed = [preprocess_text(text) for text in texts]
        self.vectorizer.fit(processed)

    def transform(self, text: str):
        processed = preprocess_text(text)
        return self.vectorizer.transform([processed])

# Global instance
vectorizer = Vectorizer()