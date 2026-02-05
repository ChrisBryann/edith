import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_llm_provider(model_id: str, hf_token: str):
    """Returns the model and input tokenizer for the model ID"""
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
    model = AutoModelForSequenceClassification.from_pretrained(model_id, token=hf_token)
    
    # If using "GPU", switch device to CUDA
    model.to(get_device())
    model.eval()
    
    return model, tokenizer
    
def get_llm_provider_pipeline(model_id: str, hf_token: str):
    """Returns the classifier using transformer's pipeline function"""
    classifier = pipeline("zero-shot-classification", model=model_id, token=hf_token, device=get_device())
    
    return classifier
    
