import torch
import pandas as pd
import numpy as np
from transformers import DistilBertTokenizer
import re
import warnings
warnings.filterwarnings('ignore')
import logging

logger = logging.getLogger(__name__)

class AssessmentCalculator:
    def __init__(self, model_path='ml_model/ultimate_burnout_model.pth'):
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            from ml_model.model_architecture import UltimateBurnoutClassifier
            
            self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
            self.model = UltimateBurnoutClassifier()
            
            if torch.cuda.is_available():
                self.model.load_state_dict(torch.load(self.model_path))
            else:
                self.model.load_state_dict(torch.load(self.model_path, map_location=torch.device('cpu')))
            
            self.model.to(self.device)
            self.model.eval()
            logger.info("ML Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            raise
    
    def clean_text(self, text):
        if pd.isna(text):
            return ""
        text = str(text)
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'[^\w\s.,!?]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.lower()
        return text
    
    def predict_burnout(self, text):
        try:
            text = self.clean_text(text)

            encoding = self.tokenizer(
                text, 
                truncation=True, 
                padding='max_length',
                max_length=128, 
                return_tensors='pt'
            )

            with torch.no_grad():
                input_ids = encoding['input_ids'].to(self.device)
                attention_mask = encoding['attention_mask'].to(self.device)
                score = self.model(input_ids, attention_mask).item()

            if score < 0.33:
                level, color = "LOW", "🟢"
                recommendation = "Maintain healthy work habits and self-care"
            elif score < 0.67:
                level, color = "MODERATE", "🟡" 
                recommendation = "Monitor stress levels and implement coping strategies"
            else:
                level, color = "HIGH", "🔴"
                recommendation = "Seek professional support and consider workplace changes"
            
            return {
                'score': score,
                'level': level,
                'color': color,
                'recommendation': recommendation
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._fallback_scoring(text)
    
    def _fallback_scoring(self, text):
        text_lower = text.lower()
        
        positive_words = ['good', 'great', 'happy', 'energized', 'motivated', 'balanced']
        negative_words = ['exhausted', 'overwhelmed', 'burned out', 'stress', 'anxiety', 'tired']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if negative_count > positive_count:
            score = 0.7
        elif positive_count > negative_count:
            score = 0.2
        else:
            score = 0.5
            
        if score < 0.33:
            level, color = "LOW", "🟢"
            recommendation = "Maintain healthy work habits and self-care"
        elif score < 0.67:
            level, color = "MODERATE", "🟡"
            recommendation = "Monitor stress levels and implement coping strategies"
        else:
            level, color = "HIGH", "🔴"
            recommendation = "Seek professional support and consider workplace changes"
        
        return {
            'score': score,
            'level': level,
            'color': color,
            'recommendation': recommendation
        }
    
    def calculate_score_from_answers(self, answers):
        combined_text = self._combine_answers(answers)
        logger.info(f"Analyzing text with ML model: {combined_text[:100]}...")
        
        result = self.predict_burnout(combined_text)
        return result
    
    def _combine_answers(self, answers):
        combined = []
        
        for field, answer in answers.items():
            if answer and len(answer.strip()) > 0:
                combined.append(answer)
        
        return " ".join(combined) if combined else "no response provided"

# Global instance
assessment_calculator = AssessmentCalculator('ml_model/ultimate_burnout_model.pth')