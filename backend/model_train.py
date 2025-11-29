import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

def load_data():
    data_frames = []
    
    # Load spam.csv
    try:
        df_spam = pd.read_csv(r'd:\TP\spam.csv', encoding='latin-1')
        # Keep only v1 (label) and v2 (text)
        df_spam = df_spam[['v1', 'v2']]
        df_spam.columns = ['label', 'text']
        data_frames.append(df_spam)
        print("Loaded spam.csv")
    except Exception as e:
        print(f"Error loading spam.csv: {e}")

    # Load Dataset_5971.csv
    try:
        df_dataset = pd.read_csv(r'd:\TP\Dataset_5971.csv')
        # Columns: LABEL, TEXT, ...
        df_dataset = df_dataset[['LABEL', 'TEXT']]
        df_dataset.columns = ['label', 'text']
        data_frames.append(df_dataset)
        print("Loaded Dataset_5971.csv")
    except Exception as e:
        print(f"Error loading Dataset_5971.csv: {e}")

    if not data_frames:
        raise ValueError("No data loaded!")

    full_df = pd.concat(data_frames, ignore_index=True)
    
    # Normalize labels
    # spam.csv uses 'ham'/'spam'
    # Dataset_5971.csv uses 'ham'/'spam' (based on quick look, but let's ensure)
    full_df['label'] = full_df['label'].str.lower().str.strip()
    
    print(f"Total samples: {len(full_df)}")
    print(full_df['label'].value_counts())
    
    return full_df

def train():
    df = load_data()
    
    X = df['text'].astype(str)
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', MultinomialNB()),
    ])
    
    print("Training model...")
    pipeline.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    # Save model
    os.makedirs(r'd:\TP\SafeEcho\backend\models', exist_ok=True)
    model_path = r'd:\TP\SafeEcho\backend\models\spam_model.pkl'
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()
