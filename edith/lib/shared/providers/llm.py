import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_llm_provider(model_id: str, hf_token: str):
    # Returns the model and input tokenizer for the model ID
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
    model = AutoModelForSequenceClassification.from_pretrained(model_id, token=hf_token)
    
    # if using GPU, set device mode to "CUDA"
    model.to(get_device())
    
    model.eval()
    
    return model, tokenizer
    