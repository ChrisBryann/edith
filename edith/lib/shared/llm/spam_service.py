from edith.lib.shared.llm.helpers import get_llm_provider, get_device, get_llm_provider_pipeline
from edith.lib.shared.llm.constants import EMAIL_FEW_SHOT_HYPOTHESIS, EMAIL_FEW_SHOT_LABELS
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
        self.device = get_device()
        self.model, self.tokenizer = get_llm_provider(config.spam_detection_model_id, config.hf_token)
        self.classifier = get_llm_provider_pipeline(config.spam_zs_detection_model_id, config.hf_token)
        
    def detect_spam(self, texts: list[str]) -> List[SpamLLMResult]:
        """Detect whether the texts are spam or not using DistillBERT (dima806/email-spam-detection-roberta)"""
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
            id_map = getattr(self.model.config, "id2label", {0: "No spam", 1: "Spam"})  # {0: "ham", 1: "spam"}
            pred_ids = probs.argmax(dim=-1).tolist()
            
            results: List[SpamLLMResult] = []
            for i, pred_id in enumerate(pred_ids):
                label = id_map[int(pred_id)]
                score = float(probs[i, pred_id])
                results.append(SpamLLMResult(label=label, score=score))

            return results
        except Exception as e:
            raise Exception(f"spam_service.detect_spam - Error trying to classify text as spam: {e}")
    
    def detect_spam_zero_shot(self, text: str) -> SpamLLMResult:
        """
        Detects whether the texts are spam or not using Zero Shot Classification with MNLI (joeddav/xlm-roberta-large-xnli)
        WARNING: HEAVY COMPUTATION USAGE, advised to use GPU instead of CPU
        """
        try:
            output = self.classifier(text, candidate_labels=EMAIL_FEW_SHOT_LABELS, hypothesis_template=EMAIL_FEW_SHOT_HYPOTHESIS)
            
            # get the index of the highest probability
            pred_idx = int(torch.argmax(output['scores']).item())
            
            return SpamLLMResult(label=output['labels'][pred_idx], score=output['scores'][pred_idx])
            
        except Exception as e:
            raise Exception(f"spam_service.detect_spam_zero_shot - Error trying to classify text as spam: {e}") from e