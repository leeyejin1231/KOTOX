# Load model directly
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("textdetox/xlmr-large-toxicity-classifier-v2")
model = AutoModelForSequenceClassification.from_pretrained("textdetox/xlmr-large-toxicity-classifier-v2")