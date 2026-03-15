import json
import os
from dotenv import load_dotenv
from engine import ResendMessenger

def run_test():
    load_dotenv()
    resend_key = os.getenv("RESEND_API_KEY")
    TARGET_EMAIL = "mattfuller85@gmail.com"
    
    if not resend_key:
        print("❌ RESEND_API_KEY missing from .env")
        return

    # Load the mock daily audits from the web dashboard data directory to simulate a week's worth of bills
    json_path = os.path.join(os.path.dirname(__file__), "web", "src", "data", "daily_audits.json")
    
    if not os.path.exists(json_path):
        print(f"❌ Could not find {json_path}. Run pipeline.py first to generate mock data.")
        return
        
    with open(json_path, "r") as f:
        audits = json.load(f)

    if not audits:
        print("❌ No audits found in the JSON file.")
        return

    print(f"Found {len(audits)} audited bills. Generating Friday Newsletter...")
    messenger = ResendMessenger(resend_key)
    success = messenger.send_weekly_briefing(audits, TARGET_EMAIL)
    
    if success:
        print("✅ Friday Test Complete! Check your inbox.")

if __name__ == "__main__":
    run_test()
