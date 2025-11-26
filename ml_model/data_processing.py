import pandas as pd
import numpy as np
import re
from torch.utils.data import Dataset
from transformers import DistilBertTokenizer

def clean_text(text):
    """Clean review text"""
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s.,!?]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.lower()
    return text

def simple_burnout_classification(score):
    """Simple classification without borderline cases"""
    if score < 0.35:
        return "LOW", "🟢"
    elif score < 0.65:
        return "MODERATE", "🟡"
    else:
        return "HIGH", "🔴"

def ultimate_label_mapping(df, label_col):
    """Ultimate label mapping"""
    label_mapping = {
        "Category 1: 'Risk' (Low performance, Low potential)": 0.98,
        "Category 2: 'Average performer' (Moderate performance, Low potential)": 0.90,
        "Category 4: 'Inconsistent Player' (Low performance, Moderate potential)": 0.82,
        "Category 5: 'Core Player' (Moderate performance, Moderate potential)": 0.50,
        "Category 7: 'Potential Gem' (Low performance, High potential)": 0.58,
        "Category 8: 'High Potential' (Moderate performance, High potential)": 0.42,
        "Category 3: 'Solid Performer' (High performance, Low potential)": 0.15,
        "Category 6: 'High Performer' (High performance, Moderate potential)": 0.08,
        "Category 9: 'Star' (High performance, High potential)": 0.02
    }
    df['burnout_score'] = df[label_col].map(label_mapping)
    return df

class BurnoutDataset(Dataset):
    """PyTorch Dataset for burnout detection"""
    def __init__(self, texts, scores, tokenizer, max_length=128):
        self.texts = texts
        self.scores = scores
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        score = self.scores[idx]

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'score': torch.tensor(score, dtype=torch.float)
        }