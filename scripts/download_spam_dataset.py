"""
Helper script to download the spam detection dataset from HuggingFace.

This requires a valid HF_TOKEN. Make sure to:
1. Add your HuggingFace token to .env: HF_TOKEN=hf_xxxxx
2. Request access to the dataset at:
   https://huggingface.co/datasets/jason23322/high-accuracy-email-classifier
3. Run this script: python scripts/download_spam_dataset.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()

HF_TOKEN = os.getenv('HF_TOKEN')
DATASET_URL = "https://huggingface.co/datasets/jason23322/high-accuracy-email-classifier/resolve/main/full_dataset.csv"
OUTPUT_DIR = Path("tests/datasets")
OUTPUT_FILE = OUTPUT_DIR / "full_emails_dataset.csv"

def download_dataset():
    if not HF_TOKEN or HF_TOKEN == "YOUR_HF_TOKEN_HERE":
        print("❌ Error: HF_TOKEN not set in .env file")
        print("\n📝 To fix this:")
        print("1. Get your token from https://huggingface.co/settings/tokens")
        print("2. Add it to .env: HF_TOKEN=hf_xxxxxxxxxxxxx")
        sys.exit(1)
    
    # Ensure directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Downloading dataset from HuggingFace...")
    print(f"   URL: {DATASET_URL}")
    print(f"   Output: {OUTPUT_FILE}")
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        response = requests.get(DATASET_URL, headers=headers, stream=True)
        response.raise_for_status()
        
        # Download with progress
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(OUTPUT_FILE, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    percent = (downloaded / total_size) * 100
                    print(f"\r   Progress: {percent:.1f}%", end='', flush=True)
        
        print("\n✅ Dataset downloaded successfully!")
        print(f"   Location: {OUTPUT_FILE}")
        print(f"   Size: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("\n❌ Authentication failed. Your HF_TOKEN may be invalid.")
            print("\n📝 Please check:")
            print("1. Token is correct in .env")
            print("2. You have access to the dataset (request at the HF page)")
        elif e.response.status_code == 404:
            print("\n❌ Dataset not found or you don't have access.")
            print("\n📝 Request access at:")
            print("   https://huggingface.co/datasets/jason23322/high-accuracy-email-classifier")
        else:
            print(f"\n❌ Download failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_dataset()
