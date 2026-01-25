import os
from dotenv import load_dotenv
from google import genai

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        return

    print(f"🔑 Using API Key: {api_key[:5]}...{api_key[-5:]}")
    print("⏳ Connecting to Google API...")
    
    try:
        client = genai.Client(api_key=api_key)
        
        print("\n🔍 Available Models (supporting 'generateContent'):")
        print("-" * 60)
        print(f"{'Model Name':<30} | {'Display Name'}")
        print("-" * 60)
        
        # List models
        pager = client.models.list()
        
        count = 0
        for model in pager:
            clean_name = model.name.replace("models/", "")
            
            # Filter for Gemini models
            if "gemini" in clean_name.lower():
                display_name = getattr(model, 'display_name', '') or clean_name
                print(f"{clean_name:<30} | {display_name}")
                count += 1
                
        print("-" * 60)
        print(f"✅ Found {count} available models.")
        print("\n👉 Update GEMINI_MODEL in your .env file with one of the names above.")
            
    except Exception as e:
        print(f"\n❌ Error listing models: {e}")
        print("\nTroubleshooting:")
        print("1. Check if your API key is correct.")
        print("2. Ensure 'Generative Language API' is enabled in Google Cloud Console.")

if __name__ == "__main__":
    main()