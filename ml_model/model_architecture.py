import torch.nn as nn
from transformers import DistilBertForSequenceClassification
import warnings
import logging

# Suppress the specific warning
warnings.filterwarnings("ignore", message="Some weights of.*were not initialized")
logging.getLogger("transformers").setLevel(logging.ERROR)

class UltimateBurnoutClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        
        # Suppress warnings for this specific call
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.encoder = DistilBertForSequenceClassification.from_pretrained(
                'distilbert-base-uncased',
                num_labels=1,
                ignore_mismatched_sizes=True
            )
        
        # Strategic freezing
        for name, param in self.encoder.named_parameters():
            if any(f'layer.{i}' in name for i in [3, 4, 5]):
                param.requires_grad = True
            else:
                param.requires_grad = False

        # Advanced classification head
        self.encoder.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(768, 1024),
            nn.GELU(),
            nn.LayerNorm(1024),
            nn.Dropout(0.2),
            nn.Linear(1024, 512),
            nn.GELU(),
            nn.LayerNorm(512),
            nn.Dropout(0.1),
            nn.Linear(512, 256),
            nn.GELU(),
            nn.LayerNorm(256),
            nn.Dropout(0.1),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        return outputs.logits.squeeze()