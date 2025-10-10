import torch.nn as nn
from transformers import AutoModel, XLMRobertaModel


class CustomBERT(nn.Module):
    def __init__(self, bert_model_name, hidden_dim, e=1e-3):
        super(CustomBERT, self).__init__()

        try:
            self.bert = AutoModel.from_pretrained(bert_model_name)
        except:
            print(f"AutoModel failed, trying XLMRobertaModel for {bert_model_name}")
            self.bert = XLMRobertaModel.from_pretrained(bert_model_name)
        self.hidden_dim = hidden_dim

        # Classifier
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(hidden_dim, 2)  # non-hate(0) / hate(1) 

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        cls_embedding = self.dropout(outputs.last_hidden_state[:, 0, :])

        logits = self.classifier(cls_embedding)
        return logits



    