from ..providers.llm import get_llm_provider, get_device
from edith.config import EmailAssistantConfig

import torch
from dataclasses import dataclass
from typing import List, Literal

@dataclass
class SpamLLMResult:
    label: str
    score: float
    

class SpamLLMService:
    def __init__(self, config: EmailAssistantConfig):
        self.model, self.tokenizer = get_llm_provider(config.spam_detection_model_id, config.hf_token)
        self.device = get_device()
        
    def detect_spam(self, texts: list[str]) -> List[SpamLLMResult]:
        # tokenize the inputs
        try:
            inputs = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            # convert inputs to "CUDA" if using GPU
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
                
            # label mapping from the model config
            id_map = self.model.config.id2label # {0: "ham", 1: "spam"}
            pred_ids = probs.argmax(dim=-1).tolist()
            
            results: List[SpamLLMResult] = []
            for i, pred_id in enumerate(pred_ids):
                label = id_map[int(pred_id)]
                score = float(probs[i, pred_id])
                results.append(SpamLLMResult(label=label, score=score))

            return results
        except Exception as e:
            raise Exception(f"spam_service.detect_spam - Error trying to classify text as spam: {e}")
        
        