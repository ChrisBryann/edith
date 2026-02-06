import os
import time
import mlflow
import shutil
from dotenv import load_dotenv
from typing import List, Dict
from google import genai
from google.genai import types

# Import system components
from edith.config import EmailAssistantConfig
from edith.services.email.rag import EmailRAGSystem
from edith.mocks.email import DummyEmailFetcher

def setup_test_environment():
    """Sets up a clean test environment with dummy data."""
    load_dotenv()
    os.environ["EDITH_ENV"] = "test"
    
    config = EmailAssistantConfig()
    
    # Clean start
    if os.path.exists(config.chroma_db_path):
        shutil.rmtree(config.chroma_db_path)
        
    rag = EmailRAGSystem(config)
    
    # Ingest Golden Dataset using new Mock Architecture
    fetcher = DummyEmailFetcher(config)
    emails, _ = fetcher.get_emails(max_results=100)
    rag.index_emails(emails)
    
    return rag, config

def llm_judge(client, model: str, question: str, ground_truth: str, prediction: str) -> float:
    """
    Uses an LLM to act as an impartial judge to score the RAG output.
    Returns a score between 0.0 and 1.0.
    """
    prompt = f"""
    You are an impartial judge evaluating an AI assistant.
    
    Question: {question}
    Ground Truth Information: {ground_truth}
    AI Prediction: {prediction}
    
    Compare the AI Prediction to the Ground Truth. 
    - If the prediction conveys the same key information as the ground truth, give a score of 1.0.
    - If it is partially correct but missing key details, give 0.5.
    - If it is wrong or irrelevant, give 0.0.
    
    Return ONLY the numeric score (0.0, 0.5, or 1.0).
    """
    
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.0)
        )
        score_str = response.text.strip()
        return float(score_str)
    except Exception as e:
        print(f"⚠️ Judge Error: {e}")
        return 0.0

def run_evaluation():
    print("🧪 Starting MLOps Evaluation Pipeline...")
    
    # 1. Setup
    rag, config = setup_test_environment()
    judge_client = genai.Client(api_key=config.gemini_api_key)
    
    # 2. Define Golden Dataset (Question + Ground Truth) - Updated to match new mock data
    eval_dataset = [
        {
            "question": "When is the Phoenix launch meeting?",
            "ground_truth": "The launch meeting is at 2 PM today (Go/No-Go meeting)."
        },
        {
            "question": "Did we get QA sign-off?",
            "ground_truth": "Yes, Dave gave the GREEN light for the launch."
        },
        {
            "question": "When is my dentist appointment?",
            "ground_truth": "Your dentist appointment is at 4:30 PM today."
        },
        {
            "question": "Do we have dinner plans?",
            "ground_truth": "Yes, sushi plans at 7:30 PM."
        },
        {
            "question": "What is the budget for Project Phoenix?",
            "ground_truth": "I couldn't find any relevant emails regarding the budget."
        }
    ]

    # 3. Start MLflow Experiment
    mlflow.set_experiment("Edith_RAG_Evaluation")
    
    with mlflow.start_run():
        # Log Parameters (Configuration)
        mlflow.log_param("model", config.gemini_model)
        mlflow.log_param("temperature", 0.3) # Hardcoded in email_rag.py
        mlflow.log_param("dataset_size", len(eval_dataset))
        
        total_score = 0
        total_latency = 0
        
        print("\n📝 Evaluating...")
        for item in eval_dataset:
            q = item["question"]
            truth = item["ground_truth"]
            
            # Run RAG
            start_time = time.time()
            # Get detailed result including sources for MLOps visibility
            result = rag.answer_question(q, return_sources=True)
            latency = time.time() - start_time
            
            if isinstance(result, dict):
                prediction = result["answer"]
                sources = result["sources"]
            else:
                prediction = result
                sources = []
            
            # Run Judge
            score = llm_judge(judge_client, config.gemini_model, q, truth, prediction)
            
            # Log individual results (optional, good for debugging)
            print(f"   Q: {q[:30]}... | Score: {score} | Latency: {latency:.2f}s")
            
            total_score += score
            total_latency += latency
            
            # Log detailed trace as artifact for debugging
            trace = {
                "question": q,
                "ground_truth": truth,
                "prediction": prediction,
                "score": score,
                "latency": latency,
                "retrieved_sources": sources
            }
            mlflow.log_dict(trace, f"traces/q_{q[:10].replace(' ', '_')}.json")

        # Calculate Aggregates
        avg_score = total_score / len(eval_dataset)
        avg_latency = total_latency / len(eval_dataset)
        
        # Log Metrics to MLflow
        mlflow.log_metric("avg_correctness_score", avg_score)
        mlflow.log_metric("avg_latency_seconds", avg_latency)
        
        print("\n" + "="*40)
        print(f"📊 Evaluation Complete")
        print(f"   Average Correctness: {avg_score:.2f} / 1.0")
        print(f"   Average Latency:     {avg_latency:.2f}s")
        print(f"   MLflow Run ID:       {mlflow.active_run().info.run_id}")
        print("="*40)
        print("👉 Run 'mlflow ui' to view results dashboard.")

if __name__ == "__main__":
    run_evaluation()