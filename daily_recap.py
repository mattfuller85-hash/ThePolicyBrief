import os
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from engine import FinancialAuditor, ResendDelivery
from dotenv import load_dotenv

def read_todays_audits() -> List[Dict[str, Any]]:
    """Reads the daily_audits.json and filters for bills processed today."""
    audit_file = 'web/src/data/daily_audits.json'
    if not os.path.exists(audit_file):
        print("No daily_audits.json found.")
        return []
        
    with open(audit_file, 'r', encoding='utf-8') as f:
        audits = json.load(f)
        
    todays_audits = []
    # Eastern time
    today_date_str = datetime.now(timezone(timedelta(hours=-5))).strftime("%Y-%m-%d")
    
    for audit in audits:
        # If we have an audit date, filter by today
        if 'audit_date' in audit and audit['audit_date'].startswith(today_date_str):
            todays_audits.append(audit)
            
    return todays_audits

def save_recap(script_data: Dict[str, Any]):
    """Saves the recap script to a JSON file."""
    recap_file = 'web/src/data/daily_recaps.json'
    recaps = []
    if os.path.exists(recap_file):
        with open(recap_file, 'r', encoding='utf-8') as f:
            recaps = json.load(f)
            
    # Add timestamp
    script_data['timestamp'] = datetime.now(timezone.utc).isoformat()
    # Insert at beginning
    recaps.insert(0, script_data)
    
    # Keep only the last 30 days
    recaps = recaps[:30]
    
    with open(recap_file, 'w', encoding='utf-8') as f:
        json.dump(recaps, f, indent=2)

def main():
    print("Starting Daily Recap Generation...")
    
    audits = read_todays_audits()
    if not audits:
        print("No bills audited today. Exiting.")
        return
        
    print(f"Found {len(audits)} bills audited today. Generating recap...")
    
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    resend_key = os.getenv("RESEND_API_KEY")

    if not gemini_key:
        print("❌ GEMINI_API_KEY missing. Exiting.")
        return

    auditor = FinancialAuditor(api_key=gemini_key)
    script_data, anchor_name = auditor.generate_daily_summary_script(audits)
    
    if not script_data:
        print("❌ Failed to generate daily recap script.")
        return
        
    print(f"✅ Generated daily recap script: {script_data.get('title')}")
    
    # Save the recap
    save_recap(script_data)
    
    # Send email
    target_email = "mattfuller85@gmail.com"
    if resend_key:
        delivery = ResendDelivery(api_key=resend_key)
        delivery.deliver_daily_summary(script_data, anchor_name, target_email)
    else:
        print("⚠️ RESEND_API_KEY missing. Skipping email delivery.")

if __name__ == "__main__":
    main()
