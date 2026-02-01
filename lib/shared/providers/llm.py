import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_llm_provider(model_id: str):
    # Returns the model and input tokenizer for the model ID
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)
    
    # if using GPU, set device mode to "CUDA"
    model.to(get_device())
    
    model.eval()
    
    return model, tokenizer
    