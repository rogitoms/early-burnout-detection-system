import os
import torch
import logging
from transformers import DistilBertTokenizer
<<<<<<< HEAD
import warnings

# Suppress all warnings at the top
warnings.filterwarnings("ignore")
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'

from .model_architecture import UltimateBurnoutClassifier
=======

from .model_architecture import UltimateBurnoutClassifier
from .prediction_utils import predict_burnout_silent
>>>>>>> 6f3ffefb422d0b370699f66f63b11dd4b23f4e47

logger = logging.getLogger(__name__)

class BurnoutDetectionService:
    def __init__(self, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), 'ultimate_burnout_model.pth')
        self.load_model()
    
    def load_model(self):
<<<<<<< HEAD
        try:
            # Suppress warnings during tokenizer loading
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
                self.model = UltimateBurnoutClassifier()
            
            if os.path.exists(self.model_path):
                self.model.load_state_dict(torch.load(self.model_path, map_location=self.device), strict=False)
                self.model.to(self.device)
                self.model.eval()
                logger.info("Model loaded successfully")
            else:
                logger.warning("Model file not found")
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def predict_burnout(self, text):
        if not self.model or not self.tokenizer:
            return {"error": "Model not loaded"}
        
        try:
            # Clean text
            import re
            if not text or len(text.strip()) == 0:
                return {"error": "Empty text"}
                
            text = str(text)
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            text = re.sub(r'[^\w\s.,!?]', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            text = text.lower()

            # Tokenize and predict with warnings suppressed
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                encoding = self.tokenizer(
                    text,
                    truncation=True,
                    padding='max_length',
                    max_length=128,
                    return_tensors='pt'
                )
                
                # Predict
                with torch.no_grad():
                    input_ids = encoding['input_ids'].to(self.device)
                    attention_mask = encoding['attention_mask'].to(self.device)
                    score = self.model(input_ids, attention_mask).item()

            # Classify
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
            return {"error": str(e)}
=======
        """Load the trained model"""
        try:
            self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
            self.model = UltimateBurnoutClassifier()
            
            if os.path.exists(self.model_path):
                self.model.load_state_dict(
                    torch.load(self.model_path, map_location=self.device), 
                    strict=False
                )
                self.model.to(self.device)
                self.model.eval()
                logger.info("Model loaded successfully from %s", self.model_path)
            else:
                logger.warning("Model file not found at %s", self.model_path)
                
        except Exception as e:
            logger.error("Error loading model: %s", e)
    
    def predict_burnout(self, text):
        """Predict burnout level for given text"""
        if not self.model or not self.tokenizer:
            return {"error": "Model not loaded properly"}
        
        try:
            # Use the silent prediction function
            result = predict_burnout_silent(text, self.model_path)
            result['model_loaded'] = True
            return result
            
        except Exception as e:
            logger.error("Prediction error: %s", e)
            return {
                "error": str(e),
                "model_loaded": self.model is not None
            }
>>>>>>> 6f3ffefb422d0b370699f66f63b11dd4b23f4e47

# Global instance
burnout_service = BurnoutDetectionService()