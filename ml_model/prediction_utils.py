import torch
import warnings
import logging
from transformers import DistilBertTokenizer
from .model_architecture import UltimateBurnoutClassifier
from .data_processing import clean_text, simple_burnout_classification

def predict_burnout_silent(text, model_path='ultimate_burnout_model.pth'):
    """COMPLETELY SILENT prediction function"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        logging.getLogger("transformers").setLevel(logging.ERROR)

        tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        model = UltimateBurnoutClassifier()

        # Load model in complete silence
        model.load_state_dict(torch.load(model_path, map_location=device), strict=False)
        model.to(device)
        model.eval()

        # Clean text
        text = clean_text(text)

        # Tokenize
        encoding = tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors='pt'
        )

        # Predict
        with torch.no_grad():
            input_ids = encoding['input_ids'].to(device)
            attention_mask = encoding['attention_mask'].to(device)
            score = model(input_ids, attention_mask).item()

    # Use SIMPLE classification
    level, color = simple_burnout_classification(score)

    # Enhanced recommendations
    if level == "LOW":
        recommendation = "Maintain healthy work habits and self-care routines"
    elif level == "MODERATE":
        recommendation = "Implement stress management strategies and consider workload adjustments"
    else:  # HIGH
        recommendation = "Seek professional support immediately and consider workplace changes"

    return {
        'score': score,
        'level': level,
        'color': color,
        'recommendation': recommendation
    }