import torch.nn as nn
from transformers import DistilBertForSequenceClassification
import torch

class UltimateBurnoutClassifier(nn.Module):
    """Ultimate burnout classifier with advanced architecture"""
    def __init__(self):
        super().__init__()
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

class FocalLoss(nn.Module):
    """Focal loss for handling class imbalance"""
    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
        self.mse = nn.MSELoss(reduction='none')

    def forward(self, inputs, targets):
        mse_loss = self.mse(inputs, targets)
        pt = torch.exp(-mse_loss)
        focal_loss = self.alpha * (1-pt)**self.gamma * mse_loss

        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss