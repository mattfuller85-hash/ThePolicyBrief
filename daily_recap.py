import os
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from engine import BillAuditor
from delivery import ResendMessenger

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
    
    auditor = BillAuditor()
    script_data, anchor_name = auditor.generate_daily_summary_script(audits)
    
    if not script_data:
        print("❌ Failed to generate daily recap script.")
        return
        
    print(f"✅ Generated daily recap script: {script_data.get('title')}")
    
    # Save the recap
    save_recap(script_data)
    
    # Send email
    messenger = ResendMessenger()
    html_body = f"""
    <h1>{script_data.get('title', 'Daily Action Recap')}</h1>
    <p><b>Anchor:</b> {anchor_name}</p>
    <p><b>Description:</b> {script_data.get('description', '')}</p>
    <hr>
    <h2>Long-Form Script (7-10 minutes)</h2>
    <pre style="font-family: sans-serif; white-space: pre-wrap;">{script_data.get('script_body', '')}</pre>
    """
    
    try:
        messenger.send_email(
            subject=f"The Policy Brief: Daily Recap - {datetime.now(timezone(timedelta(hours=-5))).strftime('%b %d, %Y')}",
            html_body=html_body
        )
        print("📧 Successfully emailed daily recap.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    main()
