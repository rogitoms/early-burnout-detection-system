import os
import torch
import logging
from transformers import DistilBertTokenizer

from .model_architecture import UltimateBurnoutClassifier
from .prediction_utils import predict_burnout_silent

logger = logging.getLogger(__name__)

class BurnoutDetectionService:
    def __init__(self, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), 'ultimate_burnout_model.pth')
        self.load_model()
    
    def load_model(self):
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

# Global instance
burnout_service = BurnoutDetectionService()