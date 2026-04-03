import sys
import os
import json

# Fix paths
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.orchestrator import Orchestrator
from src.core.brand_manager import BrandManager

def run_agency_simulation():
    print("🧪 Starting Agency Pipeline Test (No-Telegram Mode)...")
    orchestrator = Orchestrator()
    brand_mgr = BrandManager()
    
    test_cases = [
        {"brand": "glowup", "agent": "content", "task": "@glowup Sabah enerjisi için bir Reels senaryosu hazırla."},
        {"brand": "holistiglow", "agent": "cmo", "task": "@holisti Markam için 3 stratejik tavsiye ver."}
    ]
    
    for case in test_cases:
        print(f"\n--- [Testing {case['brand'].upper()} | Agent: {case['agent']}] ---")
        print(f"Task: {case['task']}")
        
        try:
            # Simulate heavy lifting
            response = orchestrator.handle_request(case['task'], agent=case['agent'], chat_id=12345)
            
            print(f"✅ Response Received:\n{response}")
            
            # Check if it mentioned a video or output
            if ".mp4" in response.lower() or "outputs/" in response:
                print("📹 STATUS: Video production was triggered successfully.")
            else:
                print("📝 STATUS: Strategy/Text generated successfully.")
                
        except Exception as e:
            print(f"❌ TEST FAILED: {e}")

if __name__ == "__main__":
    run_agency_simulation()
